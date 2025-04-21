#!/usr/bin/env python3
import os
import openai
import numpy as np
from pathlib import Path
from nano_vectordb import NanoVectorDB
from pprint import pprint

# -----------------------
# Config
# -----------------------
openai.api_key = os.environ["OPENAI_API_KEY"]
VDB_FILE = "/home/js/lgt/VideoRAG/_audiorag_workdir/vdb_chunks.json"  # ← change to your actual path
TOP_K = 5

# -----------------------
# Step 1: Load the vector DB
# -----------------------
vdb = NanoVectorDB(embedding_dim=1536, storage_file=VDB_FILE)

# -----------------------
# Step 2: Ask your question
# -----------------------
question = input("What is the relationship between busyness and effectiveness? Please use the video as your only source of information when answering. Please provide the beginning and ending of all video segments which are used in your answer.").strip()

# -----------------------
# Step 3: Embed it
# -----------------------
resp = openai.embeddings.create(
    model="text-embedding-ada-002",
    input=[question]
)
query_vec = np.array(resp.data[0].embedding, dtype=np.float32)

# -----------------------
# Step 4: Query the VDB
# -----------------------
results = vdb.query(query_vec, top_k=TOP_K)

print(f"\n🔍 Top {TOP_K} Matches:\n")
for i, item in enumerate(results, 1):
    meta = item["metadata"]
    print(f"🔹 [{i}] {meta.get('title', 'No Title')}")
    print(f"    ↳ Time: {meta.get('start_time')}s – {meta.get('end_time')}s")
    print(f"    ↳ URL:  {meta.get('url', '')}")
    print(f"    ↳ Text: {item['content']}")
    print()
