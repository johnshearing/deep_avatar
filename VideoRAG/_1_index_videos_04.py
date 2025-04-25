#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import argparse
import logging
import time
import multiprocessing
from datetime import datetime, timedelta
from pathlib import Path

from yt_dlp import YoutubeDL
from videorag import VideoRAG
from videorag._llm import openai_4o_mini_config

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

def download_video(url: str, mp4_dir: Path) -> Path:
    mp4_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
        "outtmpl": str(mp4_dir / "%(id)s.%(ext)s"),
        "quiet": True
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
    return mp4_dir / f"{info['id']}.mp4"

def convert_wav_to_mp4(wav_path: Path, image_path: str, output_path: Path):
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", "2",
        "-i", image_path,
        "-i", str(wav_path),
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output_path)
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"❌ ffmpeg failed: {result.stderr.decode()}")

def get_video_urls(args) -> list[str]:
    if args.channel_url:
        res = subprocess.run(
            ['yt-dlp', '--flat-playlist', '--print', 'id', args.channel_url],
            capture_output=True, text=True, check=True
        )
        ids = res.stdout.splitlines()
        return [f"https://www.youtube.com/watch?v={vid}" for vid in ids]
    else:
        with open(args.urls_file) as f:
            return [line.strip() for line in f if line.strip()]

def main():
    multiprocessing.set_start_method('spawn', force=True)
    start_time = time.time()

    parser = argparse.ArgumentParser(description="RAG indexer: audio-only or full video.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--channel-url", help="YouTube channel videos page URL")
    group.add_argument("--urls-file",   help="Text file with one video URL per line")

    parser.add_argument("--audio-dir",      default="_audio",            help="Where to save .wav files")
    parser.add_argument("--mp4-dir",        default="_mp4_files",        help="Where to save MP4s")
    parser.add_argument("--workdir",        default="_videorag-workdir", help="Directory for RAG outputs")
    parser.add_argument("--starting-index", type=int, default=0,         help="Index of first video to process")
    parser.add_argument("--ending-index",   type=int, default=None,      help="Index of last video to process (inclusive)")
    parser.add_argument("--enable-video",   action="store_true",        help="Download & process real video (not just audio)")

    args = parser.parse_args()

    urls = get_video_urls(args)
    end_i = args.ending_index + 1 if args.ending_index is not None else len(urls)
    to_process = urls[args.starting_index:end_i]

    print(f"\n📺 Processing videos {args.starting_index}–{end_i-1}, total {len(to_process)}\n")

    audio_dir = Path(args.audio_dir)
    mp4_dir   = Path(args.mp4_dir)
    rag       = VideoRAG(llm=openai_4o_mini_config, working_dir=args.workdir)

    for idx, url in enumerate(to_process, start=args.starting_index):
        print(f"🔢 [{idx}] {url}")
        meta = fetch_metadata(url)
        if not meta:
            print("⚠️ Skipping (metadata failed).")
            continue

        if args.enable_video:
            # — full video download —
            mp4_path = download_video(url, mp4_dir)
        else:
            # — audio-only: download wav + fake MP4 —
            wav = download_audio(url, audio_dir)
            mp4_path = mp4_dir / f"{wav.stem}.mp4"
            if not mp4_path.exists():
                print("🎞️ Generating fake MP4 from audio…")
                convert_wav_to_mp4(wav, BLANK_IMAGE_PATH, mp4_path)

        print("📥 Inserting into VideoRAG…")
        rag.insert_video(video_path_list=[str(mp4_path)])
        print("✅ Indexed:", mp4_path.name)

    # report run time
    dt = timedelta(seconds=round(time.time() - start_time))
    hours, rem = divmod(dt.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    print(f"\n⏱️  Completed in {hours}h {minutes}m {seconds}s")

if __name__ == "__main__":
    main()
