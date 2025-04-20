from videorag import VideoRAG
from videorag._llm import openai_4o_mini_config

rag = VideoRAG(llm=openai_4o_mini_config, working_dir="_audiorag_workdir")
rag.load_caption_model(debug=True)

print("🎯 chunks_vdb type:", type(rag.chunks_vdb))
print("🧪 dir(chunks_vdb):", dir(rag.chunks_vdb))