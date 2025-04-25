import os
import logging
import warnings
import time
from datetime import datetime, timedelta
from videorag._llm import openai_4o_mini_config
from videorag import VideoRAG, QueryParam

warnings.filterwarnings("ignore")
logging.getLogger("httpx").setLevel(logging.WARNING)

# Set this only if your API key isn't in the environment already
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"

def main():
    start_time = time.time()

    # 🧠 Define your question here

    query = (
        "In the video titled with Charles Hoskinson or with YouTube ID 9xf-RcWQLDI, "
        "what questions were asked of Charles and what were his answers? "
        "Please summarize each answer."
    )    

    # 🧰 Initialize VideoRAG (this will load kvs, vdbs, graph, etc.)
    rag = VideoRAG(llm=openai_4o_mini_config, working_dir="./_audiorag_workdir")
    rag.load_caption_model(debug=False)

    # 🗣️ Set up query options
    param = QueryParam(mode="videorag")
    param.wo_reference = True # include timestamps or not.

    # 🔍 Perform query
    response = rag.query(query=query, param=param)

    # 📢 Display results
    print("\n🧠 Answer:")
    print(response)

    end_time = time.time()
    run_time_seconds = end_time - start_time

    run_time_timedelta = timedelta(seconds=run_time_seconds)
    hours = run_time_timedelta.seconds // 3600
    minutes = (run_time_timedelta.seconds % 3600) // 60
    seconds = round(run_time_timedelta.seconds % 60)

    print(f"The script took {hours} hours, {minutes} minutes, and {seconds} seconds to run.")    

if __name__ == "__main__":
    main()
