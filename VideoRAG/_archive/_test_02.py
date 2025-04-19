from videorag import VideoRAG
rag = VideoRAG(llm=openai_4o_mini_config, working_dir="./testdir")
print(dir(rag))