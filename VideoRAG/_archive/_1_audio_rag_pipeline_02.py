#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import argparse
import logging
import shutil
from pathlib import Path
from datetime import datetime

from yt_dlp import YoutubeDL
from videorag import VideoRAG
from videorag._llm import openai_4o_mini_config

import whisper

# ────────────────────────────────────────────────────────────
# 1) Subclass VideoRAG for audio-only ingestion
# ────────────────────────────────────────────────────────────
class AudioRAG(VideoRAG):
    def __init__(self, *args, **kwargs):
        # Pass *all* args & kwargs directly to VideoRAG.__init__
        super().__init__(*args, **kwargs)

        # Now load Whisper-large
        import whisper
        print("Loading Whisper large model…")
        self.whisper_model = whisper.load_model("large")

    def insert_audio(self, audio_path: str, metadata: dict):
        print(f"  ↳ transcribing with Whisper-large…")
        res = self.whisper_model.transcribe(audio_path, temperature=0.0)
        raw_segments = res.get("segments", [])
        print(f"  ↳ got {len(raw_segments)} segments")

        for seg in raw_segments:
            start, end, text = seg["start"], seg["end"], seg["text"]
            chunk = text.strip()
            if not chunk:
                continue
            emb = self.embedder.embed([chunk])[0]
            key = f"{Path(audio_path).stem}::{int(start)}::0"
            record_meta = metadata.copy()
            record_meta.update({"start_time": start, "end_time": end})
            self.vdb_chunks.upsert(
                key=key, embedding=emb, metadata=record_meta
            )

        self._save_kvs()

# ────────────────────────────────────────────────────────────
# 2) Helper functions
# ────────────────────────────────────────────────────────────
def fetch_metadata(url: str) -> dict:
    try:
        out = subprocess.run(
            ["yt-dlp", "--dump-json", url],
            capture_output=True, text=True, check=True
        )
        info = json.loads(out.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"yt-dlp metadata failed: {e}")
        return {}

    return {
        "title":       info.get("title", ""),
        "channel":     info.get("uploader", ""),
        "url":         info.get("webpage_url", url),
        "upload_date": datetime.utcfromtimestamp(info.get("timestamp",0)).strftime("%Y-%m-%d")
    }

def download_audio(url: str, audio_dir: Path) -> Path:
    audio_dir.mkdir(exist_ok=True, parents=True)
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(audio_dir / "%(id)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
            "preferredquality": "192",
        }],
        "quiet": True
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
    return audio_dir / f"{info['id']}.wav"

# ────────────────────────────────────────────────────────────
# 3) Main with --starting-index and --ending-index
# ────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Audio‑only RAG: fetch metadata, download audio, transcribe, index."
    )
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--channel-url", help="YouTube channel videos page URL")
    grp.add_argument("--urls-file",   help="Text file with one video URL per line")

    parser.add_argument("--audio-dir",      default="audio",             help="Where to save .wav files")
    parser.add_argument("--workdir",        default="audiorag-workdir",  help="RAG data folder")
    parser.add_argument("--starting-index", type=int,   default=0,          help="First video index to process")
    parser.add_argument("--ending-index",   type=int,   default=None,       help="Last video index (inclusive)")

    args = parser.parse_args()

    # Build URL list
    if args.channel_url:
        res = subprocess.run(
            ["yt-dlp","--flat-playlist","--print","id", args.channel_url],
            capture_output=True, text=True, check=True
        )
        all_ids = res.stdout.splitlines()
        urls = [f"https://youtube.com/watch?v={vid}" for vid in all_ids]
    else:
        urls = [line.strip() for line in open(args.urls_file) if line.strip()]

    # Slice by start/end
    end = args.ending_index + 1 if args.ending_index is not None else len(urls)
    to_process = urls[args.starting_index:end]
    print(f"\n📺 Processing videos {args.starting_index}–{end-1}, total {len(to_process)}\n")

    # Init AudioRAG
    rag = AudioRAG(
        llm=openai_4o_mini_config,
        working_dir=args.workdir
    )
    rag.load_caption_model(debug=False)

    audio_dir = Path(args.audio_dir)
    for idx, url in enumerate(to_process, start=args.starting_index):
        print(f"[{idx}] → {url}")
        meta = fetch_metadata(url)
        if not meta:
            continue
        wav = download_audio(url, audio_dir)
        rag.insert_audio(str(wav), metadata=meta)
        wav.unlink(missing_ok=True)

    print("\n✅ Done indexing.")

if __name__ == "__main__":
    main()
