#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import argparse
import logging
import shutil
import time
from datetime import datetime
from pathlib import Path

from yt_dlp import YoutubeDL
from videorag import VideoRAG
from videorag._llm import openai_4o_mini_config
import multiprocessing

# Path to a blank image to convert wav → mp4
BLANK_IMAGE_PATH = "_blank.jpg"

def fetch_metadata(url: str) -> dict:
    try:
        out = subprocess.run(
            ["yt-dlp", "--dump-json", url],
            capture_output=True, text=True, check=True
        )
        info = json.loads(out.stdout)
        return {
            "title":       info.get("title", ""),
            "channel":     info.get("uploader", ""),
            "url":         info.get("webpage_url", url),
            "upload_date": datetime.utcfromtimestamp(info.get("timestamp", 0)).strftime("%Y-%m-%d")
        }
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Failed to fetch metadata: {e}")
        return {}

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

def convert_wav_to_mp4(wav_path: Path, image_path: str, output_path: Path):
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", "2",
        "-i", image_path,
        "-i", str(wav_path),
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output_path)
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"❌ ffmpeg failed: {result.stderr.decode()}")

def get_video_urls(args) -> list[str]:
    if args.channel_url:
        cmd = ['yt-dlp', '--flat-playlist', '--print', 'id', args.channel_url]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        ids = res.stdout.splitlines()
        return [f"https://www.youtube.com/watch?v={vid}" for vid in ids]
    elif args.urls_file:
        with open(args.urls_file) as f:
            return [line.strip() for line in f if line.strip()]
    return []

def main():
    start_time = time.time()

    multiprocessing.set_start_method('spawn', force=True)

    parser = argparse.ArgumentParser(description="Audio-to-video full RAG indexer.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--channel-url", help="YouTube channel URL (videos tab)")
    group.add_argument("--urls-file", help="File with 1 video URL per line")

    parser.add_argument("--audio-dir", default="audio", help="Where to store .wav files")
    parser.add_argument("--workdir", default="videorag-workdir", help="Directory for all RAG outputs")
    parser.add_argument("--starting-index", type=int, default=0)
    parser.add_argument("--ending-index", type=int, default=None)

    args = parser.parse_args()

    urls = get_video_urls(args)
    end_index = args.ending_index + 1 if args.ending_index is not None else len(urls)
    urls_to_process = urls[args.starting_index:end_index]

    print(f"\n📺 Processing videos {args.starting_index} to {end_index-1} (total {len(urls_to_process)})")

    audio_dir = Path(args.audio_dir)
    mp4_dir = Path("mp4_files")
    mp4_dir.mkdir(exist_ok=True)

    rag = VideoRAG(llm=openai_4o_mini_config, working_dir=args.workdir)

    for idx, url in enumerate(urls_to_process, start=args.starting_index):
        print(f"\n🔢 [{idx}] {url}")
        meta = fetch_metadata(url)
        if not meta:
            print("⚠️ Skipping due to metadata fetch failure.")
            continue

        wav_path = download_audio(url, audio_dir)
        video_id = wav_path.stem
        mp4_path = mp4_dir / f"{video_id}.mp4"

        if not mp4_path.exists():
            print("🎞️ Generating fake MP4...")
            convert_wav_to_mp4(wav_path, BLANK_IMAGE_PATH, mp4_path)

        print("📥 Inserting into VideoRAG...")
        rag.insert_video(video_path_list=[str(mp4_path)])

        print("✅ Indexed:", mp4_path.name)

    end_time = time.time()
    run_time_seconds = end_time - start_time

    run_time_timedelta = datetime.timedelta(seconds=run_time_seconds)
    hours = run_time_timedelta.seconds // 3600
    minutes = (run_time_timedelta.seconds % 3600) // 60
    seconds = round(run_time_timedelta.seconds % 60)

    print(f"The script took {hours} hours, {minutes} minutes, and {seconds} seconds to run.")         

if __name__ == "__main__":
    main()
