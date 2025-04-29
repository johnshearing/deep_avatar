#!/usr/bin/env python3
import os
import json
import logging
import warnings
import multiprocessing
import asyncio
from pathlib import Path

from videorag import VideoRAG, QueryParam
from videorag._llm import openai_4o_mini_config

warnings.filterwarnings("ignore")
logging.getLogger("httpx").setLevel(logging.WARNING)

async def main():
    # 🎯 1. Initialize
    rag = VideoRAG(llm=openai_4o_mini_config, working_dir="_videorag_workdir")
    rag.load_caption_model(debug=True)

    # 🧠 2. First Stage: Get raw chunks
    query = (
        "Retrieve all chunks from the video with YouTube ID 9xf-RcWQLDI "
        "where Charles Hoskinson reads audience questions aloud and gives answers."
    )

    param_stage1 = QueryParam(mode="videorag")
    param_stage1.only_need_context = True
    param_stage1.wo_reference = True
    param_stage1.top_k = 50

    print("\n🔍 Retrieving raw chunks...\n")
    response_chunks = await rag.aquery(query=query, param=param_stage1)

    # ⚡ Hotfix: Check type and optionally remove visual segments
    if isinstance(response_chunks, list):
        if rag.caption_model is None:
            print("⚠️ No caption model loaded, removing video segments from results.")
            response_chunks = [chunk for chunk in response_chunks if chunk.get("source_type") != "video_segment"]
    else:
        print("❌ Unexpected result format, expected a list of chunks!")
        print("Actual type:", type(response_chunks))
        print("Actual content:", response_chunks)

        # Save unexpected output
        with open("_debug_unexpected_response.json", "w") as f:
            json.dump({"response": str(response_chunks)}, f, indent=2)

        print("\n⚠️ Saved unexpected response to _debug_unexpected_response.json")
        exit(1)

    # 🧹 Check if response is valid
    if not isinstance(response_chunks, list):
        print("❌ Unexpected result format, expected a list of chunks!")
        print("Actual type:", type(response_chunks))
        print("Actual content:", response_chunks)


        print("\n🔎 Debugging Info:")
        print("response_chunks type:", type(response_chunks))
        print("response_chunks value (truncated):", str(response_chunks)[:500])  # Print only first 500 chars

        
        # Save the unexpected output to a file so we can inspect it
        with open("_debug_unexpected_response.json", "w") as f:
            json.dump(response_chunks, f, indent=2)
        print("\n⚠️ Saved unexpected response to _debug_unexpected_response.json")
        exit(1)

    # 📄 Save retrieved chunks to file
    save_path = Path("_retrieved_chunks.json")
    with open(save_path, "w") as f:
        json.dump(response_chunks, f, indent=2)

    print(f"\n✅ Retrieved {len(response_chunks)} chunks and saved to {save_path}\n")

    # 📋 OPTIONAL: Print a mini table of chunks
    print("\n📋 Extracted Chunks Summary:\n")
    for idx, chunk in enumerate(response_chunks, 1):
        text = chunk.get("content", "")[:120].replace("\n", " ").strip()
        print(f"[{idx}] {text}...")

    # 🧠 3. Second Stage: Synthesize final answer
    print("\n🛠️ Building follow-up query from chunks...")

    context_text = "\n\n".join(
        chunk.get("content", "") for chunk in response_chunks if isinstance(chunk, dict)
    )

    followup_query = (
        "Based only on the following extracted text chunks from the video, "
        "list the questions Charles Hoskinson answered and give a short summary for each.\n\n"
        + context_text
    )

    param_stage2 = QueryParam(mode="videorag")
    param_stage2.only_need_context = False
    param_stage2.wo_reference = False

    print("\n🤖 Final LLM query in progress...\n")
    final_response = await rag.aquery(query=followup_query, param=param_stage2)

    print("\n🧠 Final synthesized answer:\n")
    print(final_response)

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
    asyncio.run(main())
