import os
import sys
import json
import subprocess
import argparse
import logging
from pathlib import Path
from datetime import datetime

from yt_dlp import YoutubeDL
from videorag import VideoRAG, QueryParam
from videorag._llm import openai_4o_mini_config
from videorag._videoutil.caption import segment_caption


# ----------------------
# Subclass AudioRAG
# ----------------------
class AudioRAG(VideoRAG):
    """
    Audio-only RAG: transcribes audio, chunks text, embeds, and stores with metadata.
    """

    def __init__(self, *args, **kwargs):
        # Call parent constructor (this sets self.embedder, etc.)
        super().__init__(*args, **kwargs)

        # 🔥 Important: Call the VideoRAG init method
        self.init()  # ← THIS IS THE MISSING PIECE

        # Load Whisper-large for audio transcription
        import whisper
        print("Loading Whisper large model…")
        self.whisper_model = whisper.load_model("large")



    def insert_audio(self, audio_path: str, metadata: dict):
        # ensure caption_model is loaded
        if not hasattr(self, 'caption_model') or self.caption_model is None:
            self.load_caption_model(debug=False)

        print(f"Transcribing audio: {audio_path}")
        # ← here, drop the `model=` keyword
        segments = segment_caption(audio_path)
        print(f"Got {len(segments)} segments from transcription.")

        # 2. Process each segment
        for start, end, transcript in segments:
            # Chunk text
            chunks = self._chunk_text(transcript)
            for i, chunk in enumerate(chunks):
                # Embed chunk
                emb = self.embedder.embed([chunk])[0]
                # Build a unique key for upsert
                key = f"{Path(audio_path).stem}::{int(start)}::{i}"
                # Add timing to metadata
                record_meta = metadata.copy()
                record_meta.update({
                    'start_time': start,
                    'end_time':   end
                })
                # Upsert into chunk vector DB
                self.vdb_chunks.upsert(key=key, embedding=emb, metadata=record_meta)

        # Persist changes
        self._save_kvs()

# ----------------------
# Helper Functions
# ----------------------
def fetch_metadata(url: str) -> dict:
    """
    Use yt-dlp to fetch metadata JSON for a YouTube URL.
    """
    try:
        result = subprocess.run(
            ['yt-dlp', '--dump-json', url],
            capture_output=True, text=True, check=True
        )
        info = json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to fetch metadata for {url}: {e}")
        return {}

    metadata = {
        'title':       info.get('title', ''),
        'channel':     info.get('uploader', ''),
        'url':         info.get('webpage_url', url),
        'upload_date': datetime.utcfromtimestamp(info.get('timestamp', 0)).strftime('%Y-%m-%d')
    }
    return metadata

def download_audio(url: str, audio_dir: Path) -> Path:
    """
    Download audio from YouTube as WAV, return path to .wav file.
    """
    audio_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(audio_dir / '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'quiet': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
    return audio_dir / f"{info['id']}.wav"

# ----------------------
# Main: Index Channel or URLs
# ----------------------
def main():
    parser = argparse.ArgumentParser(
        description='Audio-only RAG pipeline: fetch metadata, download audio, transcribe, index.'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--channel-url', help='YouTube channel videos page URL')
    group.add_argument('--urls-file', help='Path to text file with one video URL per line')

    parser.add_argument('--audio-dir', default='audio', help='Directory to store downloaded audio')
    parser.add_argument('--workdir', default='audiorag-workdir', help='Working directory for RAG indices')
    parser.add_argument('--starting-index', type=int, default=0, help='Index of first video to process')
    parser.add_argument('--ending-index', type=int, default=None, help='Index of last video to process (inclusive)')

    args = parser.parse_args()

    # Prepare list of URLs
    if args.channel_url:
        cmd = ['yt-dlp', '--flat-playlist', '--print', 'id', args.channel_url]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            ids = res.stdout.splitlines()
            urls = [f'https://www.youtube.com/watch?v={vid}' for vid in ids]
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to fetch playlist from {args.channel_url}: {e}")
            sys.exit(1)
    else:
        with open(args.urls_file) as f:
            urls = [line.strip() for line in f if line.strip()]

    # Apply index filtering
    end_index = args.ending_index + 1 if args.ending_index is not None else len(urls)
    urls_to_process = urls[args.starting_index:end_index]

    print(f"\n📺 Processing videos {args.starting_index} to {end_index - 1} (total {len(urls_to_process)})")

    # Initialize AudioRAG

    rag = AudioRAG(
        llm=openai_4o_mini_config(),
        working_dir=args.workdir
    )

    rag.load_caption_model(debug=False)

    audio_dir = Path(args.audio_dir)

    for i, url in enumerate(urls_to_process, start=args.starting_index):
        print(f"\n🔢 [{i}] Processing URL: {url}")
        meta = fetch_metadata(url)
        if not meta:
            continue
        wav = download_audio(url, audio_dir)
        rag.insert_audio(str(wav), metadata=meta)
        wav.unlink(missing_ok=True)

    print("\n✅ AudioRAG indexing complete!")


if __name__ == '__main__':
    main()
