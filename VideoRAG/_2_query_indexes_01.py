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
        "In the video with YouTube ID 9xf-RcWQLDI where Charles Hoskinson is speaking, "
        "Please list the segments where Charles discusses issues pertaining to his company IOG"
    )       

    '''
    query = (
        "In the video with YouTube ID 9xf-RcWQLDI where Charles Hoskinson is speaking, "
        "Please list the questions which were read aloud by Charles, and please summarize his answers? "
    )   


    query = (
        "In the video with YouTube ID 9xf-RcWQLDI where Charles Hoskinson is speaking, "
        "what specifically is Charles asking the Cardano community to vote for on behalf of his company IOG when the community votes on the budget proposal? "
        "What points does Charles express in the video in order to convince the voters to grant his request?"
    )     
    '''
    

    # 🧰 Initialize VideoRAG (this will load kvs, vdbs, graph, etc.)
    rag = VideoRAG(llm=openai_4o_mini_config, working_dir="./_videorag_workdir")
    rag.load_caption_model(debug=False)

    # 🗣️ Set up query options
    # {'mode': typing.Literal['local', 'global', 'naive'], 
    # 'only_need_context': <class 'bool'>, 'response_type': <class 'str'>, 'level': <class 'int'>, 'top_k': <class 'int'>}
    param = QueryParam(mode="videorag")

    # Set False if want the system to look through the video when answering.
    # Set True If you want raw chunks from the database only. 
    param.only_need_context = False
    
    # This stands for without reference. So False means "provide the timestamps when answering"
    param.wo_reference = True

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
