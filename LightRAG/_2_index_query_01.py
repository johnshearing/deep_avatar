import os
import asyncio
import logging
import logging.config
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import logger, set_verbose_debug, EmbeddingFunc
from llama_index.embeddings.openai import OpenAIEmbedding

# Load environment variables from .env file
# from dotenv import load_dotenv
# load_dotenv()

# Configuration
WORKING_DIR = "_0_jack_work_dir_01"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", 3072))
API_KEY = os.getenv("EMBEDDING_BINDING_API_KEY")
MAX_TOKEN_SIZE = int(os.getenv("MAX_TOKEN_SIZE", 8192))


def configure_logging():
    """Configure logging with console and rotating file handlers."""
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "lightrag"]:
        logger_instance = logging.getLogger(logger_name)
        logger_instance.handlers = []
        logger_instance.filters = []
    log_dir = os.getenv("LOG_DIR", os.getcwd())
    log_file_path = os.path.abspath(os.path.join(log_dir, "lightrag_query.log"))
    print(f"\nLightRAG query log file: {log_file_path}\n")
    os.makedirs(os.path.dirname(log_dir), exist_ok=True)
    log_max_bytes = int(os.getenv("LOG_MAX_BYTES", 10485760))
    log_backup_count = int(os.getenv("LOG_BACKUP_COUNT", 5))
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {"format": "%(levelname)s: %(message)s"},
                "detailed": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
            },
            "handlers": {
                "console": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "file": {
                    "formatter": "detailed",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": log_file_path,
                    "maxBytes": log_max_bytes,
                    "backupCount": log_backup_count,
                    "encoding": "utf-8",
                },
            },
            "loggers": {
                "lightrag": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }
    )
    logger.setLevel(logging.INFO)
    set_verbose_debug(os.getenv("VERBOSE_DEBUG", "true").lower() == "true")

async def initialize_rag():
    """Initialize LightRAG with custom embedding function."""
    print("Initializing LightRAG for querying...")
    
    # Initialize embedding model
    embed_model = OpenAIEmbedding(
        model=EMBEDDING_MODEL,
        api_key=API_KEY,
        dimensions=EMBEDDING_DIM
    )
    
    # Define async embedding function
    async def async_embedding_func(texts):
        return embed_model.get_text_embedding_batch(texts)
    
    # Define embedding function
    embedding_func = EmbeddingFunc(
        embedding_dim=EMBEDDING_DIM,
        max_token_size=MAX_TOKEN_SIZE,               
        func=async_embedding_func
    )
    
    # Initialize LightRAG
    rag = LightRAG(
        working_dir=WORKING_DIR,
        embedding_func=embedding_func,
        llm_model_func=gpt_4o_mini_complete
    )
    
    await rag.initialize_storages()
    await initialize_pipeline_status()
    await rag.aclear_cache()
    return rag

async def main():
    """Main function to query the LightRAG index."""
    rag = None
    try:
        if not os.getenv("OPENAI_API_KEY") and not API_KEY:
            raise ValueError("OPENAI_API_KEY or EMBEDDING_BINDING_API_KEY environment variable not set")
        rag = await initialize_rag()
        
        # Check if index exists
        if not os.path.exists(os.path.join(WORKING_DIR, "kv_store_full_docs.json")):
            raise FileNotFoundError(f"No index found in {WORKING_DIR}. Run the indexing script first.")
        
        # Perform query

        query = (
            "/mix [Time stamps in the source text appear like the following sample: [6.56 > 11.68]. The values given between the brackets are in seconds and decimal fractions of a second, not in minutes. The source text is a transcript from the source video. The URL for the source video is found in the metadata associated with the source text. So the values between the brackets in the above sample indicate a time between 6.56 seconds and 11.68 seconds into the video. Please provide URLs in your responses for source video that incorporate the timestamps found in the source text so that the videos can be viewed at the moment which is relevant to the query response. The following is an example of how the URLs should be structured if the source text is from Ln3WszTq0uA.txt and the moment of interest has a time stamp of [6.56 > 11.68]: https://www.youtube.com/watch?v=Ln3WszTq0uA&t=6s. Provide the timestamp in seconds and round the timestamp value to the nearest second] Please search for all instances where Don Scott and how did he contribute to the understanding of phases of water is discussed."
        )
      
         
        for mode in ["naive", "local", "global", "hybrid", "mix"]:  # "naive", "local", "global", "hybrid", "mix"
            print(f"\n=====================")
            print(f"Query mode: {mode}")
            print(f"=====================")
            response = await rag.aquery(
                query,
                param=QueryParam(mode=mode, top_k=50),  # top_k=50, only_need_context=True, only_need_prompt=True
            )
            print(response)
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if rag:
            print("Finalizing storages...")
            await rag.finalize_storages()

if __name__ == "__main__":
    configure_logging()
    asyncio.run(main())
    print("\nQuerying Done!")


    '''
    print("--- All Loaded Environment Variables ---")
    # os.environ is a dictionary-like object
    # You can iterate over its items (key-value pairs)
    for key, value in os.environ.items():
        print(f"{key}={value}")

    print("--------------------------------------")
    '''



