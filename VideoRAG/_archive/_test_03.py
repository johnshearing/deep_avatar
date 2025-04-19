from videorag import VideoRAG
from videorag._llm import openai_4o_mini_config

rag = VideoRAG(llm=openai_4o_mini_config, working_dir="my_test_workdir")

print("video_path_db has save():", hasattr(rag.video_path_db, "save"))
print("text_chunks has save():", hasattr(rag.text_chunks, "save"))
print("chunks_vdb has save():", hasattr(rag.chunks_vdb, "save"))