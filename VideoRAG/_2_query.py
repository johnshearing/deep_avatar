import os
import logging
import warnings
import multiprocessing

warnings.filterwarnings("ignore")
logging.getLogger("httpx").setLevel(logging.WARNING)

# Not needed here if this is already set in .bashrc
# Please enter your openai key
# os.environ["OPENAI_API_KEY"] = ""

from videorag._llm import *
from videorag import VideoRAG, QueryParam


if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')

    query = "Does a person's feelings effect what happens in that person's life?"
    param = QueryParam(mode="videorag")
    # if param.wo_reference = False, VideoRAG will add reference to video clips in the response
    param.wo_reference = True

    videorag = videorag = VideoRAG(llm=openai_4o_mini_config, working_dir=f"./videorag-workdir")
    videorag.load_caption_model(debug=False)
    response = videorag.query(query=query, param=param)
    print(response)