#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import argparse
import logging
import openai
import whisper
import numpy as np                                # ← CHANGED: import numpy
from pathlib import Path
from datetime import datetime

from yt_dlp import YoutubeDL
from videorag import VideoRAG
from videorag._llm import openai_4o_mini_config
import asyncio

# ----------------------
# Subclass AudioRAG
# ----------------------
class AudioRAG(VideoRAG):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load Whisper-large once
        print("Loading Whisper large model…")
        self.whisper_model = whisper.load_model("large")

    def insert_audio(self, audio_path: str, metadata: dict):
        openai.api_key = os.environ["OPENAI_API_KEY"]

        print(f"Transcribing audio: {audio_path}")
        result = self.whisper_model.transcribe(audio_path, temperature=0.0)
        segments = result.get("segments", [])
        print(f"Got {len(segments)} segments")

        for seg in segments:
            start, end, text = seg["start"], seg["end"], seg["text"].strip()
            if not text:
                continue

            # 1) Create embedding via OpenAI
            resp = openai.embeddings.create(
                model="text-embedding-ada-002",
                input=[text]
            )
            # 2) Cast to NumPy array to satisfy NanoVectorDB
            emb = np.array(resp.data[0].embedding, dtype=np.float32)   # ← CHANGED

            # 3) Build metadata record
            record_meta = metadata.copy()
            record_meta.update({
                "start_time": start,
                "end_time":   end
            })

            # 4) Upsert with the correct key names and structure
            self.chunks_vdb.upsert([{
                "__id__":     f"{Path(audio_path).stem}::{int(start)}::0",  # ← CHANGED
                "__vector__": emb,                                          # ← CHANGED
                **record_meta                                            # ← CHANGED: spread metadata fields
            }])


        print("🔍 ATTRIBUTES:", dir(self))            

        asyncio.run(self._save_video_segments())

# ----------------------
# Helper Functions
# ----------------------
def fetch_metadata(url: str) -> dict:
    try:
        out = subprocess.run(
            ["yt-dlp", "--dump-json", url],
            capture_output=True, text=True, check=True
        )
        info = json.loads(out.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to fetch metadata for {url}: {e}")
        return {}

    return {
        "title":       info.get("title", ""),
        "channel":     info.get("uploader", ""),
        "url":         info.get("webpage_url", url),
        "upload_date": datetime.utcfromtimestamp(info.get("timestamp", 0)).strftime("%Y-%m-%d")
    }

def download_audio(url: str, audio_dir: Path) -> Path:
    audio_dir.mkdir(parents=True, exist_ok=True)
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

# ----------------------
# Main: Index Channel or URLs
# ----------------------
def main():
    parser = argparse.ArgumentParser(
        description="Audio-only RAG pipeline: fetch metadata, download audio, transcribe, index."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--channel-url", help="YouTube channel videos page URL")
    group.add_argument("--urls-file",   help="Path to text file with one video URL per line")

    parser.add_argument("--audio-dir",      default="audio",            help="Where to save .wav files")
    parser.add_argument("--workdir",        default="audiorag-workdir", help="RAG data folder")
    parser.add_argument("--starting-index", type=int, default=0,         help="Index of first video to process")
    parser.add_argument("--ending-index",   type=int, default=None,      help="Index of last video to process (inclusive)")

    args = parser.parse_args()

    # Build list of URLs
    if args.channel_url:
        res = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--print", "id", args.channel_url],
            capture_output=True, text=True, check=True
        )
        all_ids = res.stdout.splitlines()
        urls = [f"https://youtube.com/watch?v={vid}" for vid in all_ids]
    else:
        with open(args.urls_file, "r") as f:
            urls = [line.strip() for line in f if line.strip()]

    # Slice by start/end
    end = args.ending_index + 1 if args.ending_index is not None else len(urls)
    to_process = urls[args.starting_index:end]
    print(f"\n📺 Processing videos {args.starting_index}–{end-1}, total {len(to_process)}\n")

    # Initialize AudioRAG
    rag = AudioRAG(
        llm=openai_4o_mini_config,      # pass config object
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

    print("\n✅ AudioRAG indexing complete!")

if __name__ == "__main__":
    main()
