import os
import asyncio
import logging
import logging.config
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import logger, set_verbose_debug
import textract

WORKING_DIR = "./_sonata_work_dir"
PDF_FILE_PATH = "./_docs_dir/sonata.pdf"

def configure_logging():
    """Configure logging for the application"""
    # Reset any existing handlers to ensure clean configuration
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "lightrag"]:
        logger_instance = logging.getLogger(logger_name)
        logger_instance.handlers = []
        logger_instance.filters = []

    # Get log directory path from environment variable or use current directory
    log_dir = os.getenv("LOG_DIR", os.getcwd())
    log_file_path = os.path.abspath(os.path.join(log_dir, "lightrag_demo.log"))

    print(f"\nLightRAG demo log file: {log_file_path}\n")
    os.makedirs(os.path.dirname(log_dir), exist_ok=True)

    # Get log file max size and backup count from environment variables
    log_max_bytes = int(os.getenv("LOG_MAX_BYTES", 10485760))  # Default 10MB
    log_backup_count = int(os.getenv("LOG_BACKUP_COUNT", 5))  # Default 5 backups

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(levelname)s: %(message)s",
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
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

    # Set the logger level to INFO
    logger.setLevel(logging.INFO)
    # Enable verbose debug if needed
    set_verbose_debug(os.getenv("VERBOSE_DEBUG", "false").lower() == "true")

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete,
    )
    await rag.initialize_storages()
    await initialize_pipeline_status()
    return rag

async def main():
    try:
        # Initialize RAG instance
        rag = await initialize_rag()

        # Check if index already exists
        index_exists = os.path.exists(os.path.join(WORKING_DIR, "kv_store_full_docs.json"))

        if not index_exists:
            # Process PDF file
            if not os.path.exists(PDF_FILE_PATH):
                raise FileNotFoundError(f"PDF file not found at: {PDF_FILE_PATH}")
            
            print("Indexing PDF...")
            text_content = textract.process(PDF_FILE_PATH)
            decoded_text = text_content.decode('utf-8')
            await rag.ainsert(decoded_text)
            print("Indexing complete.")
        else:
            print("Using existing index.")

        # Perform your query
        print("\n=====================")
        print("Query mode: hybrid")
        print("=====================")
        print(
            await rag.aquery(
                "Please list all the space ships that belong to the societly know as 'The Culture' and describe each one and how they relate to each other in the story.",  # Replace with your new query
                param=QueryParam(mode="hybrid"),
            )
        )
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if rag:
            await rag.finalize_storages()