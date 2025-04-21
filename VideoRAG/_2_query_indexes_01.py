import os
import logging
import warnings
from videorag._llm import openai_4o_mini_config
from videorag import VideoRAG, QueryParam

warnings.filterwarnings("ignore")
logging.getLogger("httpx").setLevel(logging.WARNING)

# Set this only if your API key isn't in the environment already
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"

def main():
    # 🧠 Define your question here
    query = (
        "Is the work 'belife' defined anywhere in video iGnBnTut2bk?"
        "If so, please provide the beginning and ending of all video segments where the word 'belife' is defined."
    )

    # 🧰 Initialize VideoRAG (this will load kvs, vdbs, graph, etc.)
    rag = VideoRAG(llm=openai_4o_mini_config, working_dir="./_audiorag_workdir")
    rag.load_caption_model(debug=False)

    # 🗣️ Set up query options
    param = QueryParam(mode="videorag")
    param.wo_reference = False  # Show references (timestamps and video URLs)

    # 🔍 Perform query
    response = rag.query(query=query, param=param)

    # 📢 Display results
    print("\n🧠 Answer:")
    print(response)

if __name__ == "__main__":
    main()
