#!/usr/bin/env python3

# This script doesn't run to completion. Rather it errors.
# Still, it has interesting ideas and would be worth debugging.

# The following is the bash run command. The query parmeter has a default in the script.
# python3 _3_query_two_stage_bonus.py --query "List everything Charles Hoskinson said about Cardano staking in video 9xf-RcWQLDI"



import os
import json
import logging
import warnings
import multiprocessing
import asyncio
from pathlib import Path
import argparse

from videorag import VideoRAG, QueryParam
from videorag._llm import openai_4o_mini_config

from termcolor import colored

warnings.filterwarnings("ignore")
logging.getLogger("httpx").setLevel(logging.WARNING)

async def main():
    # 🔹 Argument parser
    parser = argparse.ArgumentParser(description="Two-stage VideoRAG query runner with chunk inspection.")
    parser.add_argument("--query", type=str, default=None, help="Custom query instead of hardcoded default.")
    parser.add_argument("--workdir", type=str, default="_videorag_workdir", help="Path to working directory.")
    args = parser.parse_args()

    # 🎯 1. Initialize
    rag = VideoRAG(llm=openai_4o_mini_config, working_dir=args.workdir)
    rag.load_caption_model(debug=True)

    # 🧠 2. First Stage: Raw retrieval
    query_stage1 = args.query or (
        "Retrieve all chunks from the video with YouTube ID 9xf-RcWQLDI "
        "where Charles Hoskinson reads audience questions aloud and gives answers."
    )

    param_stage1 = QueryParam(mode="videorag")
    param_stage1.only_need_context = True
    param_stage1.wo_reference = True
    param_stage1.top_k = 50

    print(colored("\n🔍 Retrieving raw chunks...\n", "cyan"))
    response_chunks = await rag.aquery(query=query_stage1, param=param_stage1)

    # 🛠️ Hotfix: Remove visual-only segments if caption model disabled
    if rag.caption_model is None:
        print(colored("⚠️ No caption model loaded, removing video segments from results.\n", "yellow"))
        if isinstance(response_chunks, list):
            response_chunks = [
                chunk for chunk in response_chunks
                if chunk.get("source_type") != "video_segment"
            ]
        else:
            print(colored("❌ Unexpected result type! Saving for debug...", "red"))
            with open("_debug_unexpected_response.json", "w") as f:
                json.dump(response_chunks, f, indent=2)
            return

    # 📄 Save Stage 1 results
    save_chunks_path = Path("_retrieved_chunks.json")
    with save_chunks_path.open("w") as f:
        json.dump(response_chunks, f, indent=2)
    print(colored(f"✅ Retrieved {len(response_chunks)} chunks and saved to {save_chunks_path}\n", "green"))

    # 📋 Pretty Print Chunks Table
    print(colored("📋 Extracted Chunks Preview:\n", "magenta"))
    for idx, chunk in enumerate(response_chunks, 1):
        short_text = chunk.get("content", "").replace("\n", " ").strip()[:120]
        source = chunk.get("source_id", "Unknown ID")
        start = chunk.get("start_sec", "N/A")
        end = chunk.get("end_sec", "N/A")
        print(f"[{idx}] {source} ({start}-{end}s): {short_text}...")

    # 🧠 3. Second Stage: Build final answer
    print(colored("\n🛠️ Building follow-up query from extracted chunks...\n", "cyan"))

    context_text = "\n\n".join(
        chunk.get("content", "") for chunk in response_chunks if isinstance(chunk, dict)
    )

    followup_query = (
        "Based only on the following extracted text chunks from the video, "
        "list each question Charles Hoskinson answered and give a short summary.\n\n"
        + context_text
    )

    param_stage2 = QueryParam(mode="videorag")
    param_stage2.only_need_context = False
    param_stage2.wo_reference = False

    print(colored("\n🤖 Final LLM query in progress...\n", "cyan"))
    final_response = await rag.aquery(query=followup_query, param=param_stage2)

    # 📄 Save Stage 2 results
    save_final_txt_path = Path("_final_response.txt")
    save_final_md_path = Path("_final_response.md")

    with save_final_txt_path.open("w") as f:
        f.write(final_response)

    with save_final_md_path.open("w") as f:
        f.write("# 🧠 Final Synthesized Answer\n\n")
        f.write(final_response.replace("\n", "  \n"))  # Markdown line breaks

    print(colored(f"\n✅ Final answer saved to {save_final_txt_path} and {save_final_md_path}\n", "green"))
    print(colored("\n🧠 Final Answer Preview:\n", "magenta"))
    print(final_response[:3000])  # Show first 3000 characters

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
    asyncio.run(main())
