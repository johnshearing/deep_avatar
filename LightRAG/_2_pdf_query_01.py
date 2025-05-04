import os
import asyncio
import logging
import logging.config
import re
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_embed, gpt_4o_mini_complete
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import logger, set_verbose_debug

WORKING_DIR = "./_ts_work_dir"

def configure_logging():
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
    print("Initializing LightRAG for querying...")
    rag = LightRAG(
        working_dir=WORKING_DIR,
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete
    )
    await rag.initialize_storages()
    await initialize_pipeline_status()
    await rag.aclear_cache(modes=["naive"])
    return rag

async def main():
    rag = None
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set")
        rag = await initialize_rag()
        
        # Check if index exists
        if not os.path.exists(os.path.join(WORKING_DIR, "kv_store_full_docs.json")):
            raise FileNotFoundError(f"No index found in {WORKING_DIR}. Run the indexing script first.")
        
        # Perform query

        ''' Comented out
        query = (
            f"Using only the verbatim text, "
            "What is likely the problem if a motor is hot? "
            "Do not infer, extrapolate, or use any external knowledge. "
            "Quote relevant text verbatim."
        )
        '''

        query = "Using only the text to answer, " \
        "The Mod-Linx conveyor is stopping and starting by itself. What should I do? , "\
        "Please use only the provided text when forming your answer."

        
        all_ships = set()
        for mode in ["naive", "local", "global", "hybrid", "mix"]:
            print(f"\n=====================")
            print(f"Query mode: {mode}")
            print(f"=====================")
            response = await rag.aquery(
                query,
                param=QueryParam(mode=mode, top_k=50)
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