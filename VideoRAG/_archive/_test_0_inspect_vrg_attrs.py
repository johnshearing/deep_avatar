from videorag import VideoRAG
from videorag._llm import openai_4o_mini_config

def main():
    # instantiate with dummy working dir
    rag = VideoRAG(llm=openai_4o_mini_config, working_dir="inspect-workdir")
    # collect attributes that don’t start with “_”
    public_attrs = [attr for attr in dir(rag) if not attr.startswith("_")]
    # print them out, one per line
    print("Public attributes on VideoRAG instance:\n")
    for a in public_attrs:
        print(a)

if __name__ == "__main__":
    main()