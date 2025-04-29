#!/usr/bin/env python3
import logging
import warnings
import multiprocessing
import json

from videorag import VideoRAG, QueryParam
from videorag._llm import openai_4o_mini_config

warnings.filterwarnings("ignore")
logging.getLogger("httpx").setLevel(logging.WARNING)

def main():
    multiprocessing.set_start_method('spawn', force=True)

    # Initialize VideoRAG
    rag = VideoRAG(llm=openai_4o_mini_config, working_dir="./_audiorag_workdir")
    rag.load_caption_model(debug=False)

    # --- STEP 1: Retrieve all relevant chunks
    param = QueryParam(mode="videorag", top_k=100)
    param.only_need_context = True
    param.wo_reference = False

    query_text = (
        "In the video with Charles Hoskinson speaking or with YouTube ID 9xf-RcWQLDI, "
        "find all community questions and his answers."
    )

    print("🔎 Retrieving chunks...")
    context_result = rag.query(query=query_text, param=param)
    
    if not isinstance(context_result, list):
        print("❌ Unexpected result format, expected a list of chunks!")
        return

    # Show intermediate chunks (this is what you requested)
    print("\n--- Retrieved Chunks ---")
    for idx, chunk in enumerate(context_result):
        print(f"\nChunk {idx+1}:")
        print(json.dumps(chunk, indent=2))

    # --- STEP 2: Summarize the chunks into final answer
    merged_context = "\n\n".join([chunk["content"] for chunk in context_result])

    summarization_prompt = (
        "Below are segments from a Charles Hoskinson AMA session.\n"
        "For each question Charles answers, extract:\n"
        "- The full question text\n"
        "- A short summary of his answer\n"
        "- The start_time and end_time if provided\n"
        "\n"
        "If no question is found, skip that chunk.\n"
        "Here is the content:\n\n"
        f"{merged_context}"
    )

    # Create new param for real summarization
    summarize_param = QueryParam(mode="videorag")
    summarize_param.only_need_context = False
    summarize_param.wo_reference = True  # Don't clutter with references

    print("\n📝 Summarizing extracted chunks...")
    final_response = rag.query(query=summarization_prompt, param=summarize_param)

    print("\n--- Final Summarized Answer ---\n")
    print(final_response)

if __name__ == "__main__":
    main()
