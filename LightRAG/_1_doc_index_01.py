import os
import asyncio
import logging
import logging.config
import json
import re
from lightrag import LightRAG
from lightrag.llm.openai import gpt_4o_mini_complete
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import logger, set_verbose_debug, EmbeddingFunc
from llama_index.embeddings.openai import OpenAIEmbedding
import textract

# Configuration
WORKING_DIR = "_0_jack_work_dir_01"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", 3072))
API_KEY = os.getenv("EMBEDDING_BINDING_API_KEY")
MAX_TOKEN_SIZE = int(os.getenv("MAX_TOKEN_SIZE", 8192))

# Files to be indexed
files_2b_indexed = [
    "/home/js/lgt/LightRAG/_0_jack_processed/Ln3WszTq0uA.txt"
]

def configure_logging():
    """Configure logging with console and rotating file handlers."""
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "lightrag"]:
        logger_instance = logging.getLogger(logger_name)
        logger_instance.handlers = []
        logger_instance.filters = []
    log_dir = os.getenv("LOG_DIR", os.getcwd())
    log_file_path = os.path.abspath(os.path.join(log_dir, "lightrag_index.log"))
    print(f"\nLightRAG index log file: {log_file_path}\n")
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

if not os.path.exists(WORKING_DIR):
    os.makedirs(WORKING_DIR)

async def initialize_rag():
    """Initialize LightRAG with custom embedding function."""
    print("Initializing LightRAG for indexing...")
    
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
        llm_model_func=gpt_4o_mini_complete,
        entity_extract_max_gleaning=0
    )
    
    await rag.initialize_storages()
    await initialize_pipeline_status()
    return rag

async def main():
    """Main function to index documents."""
    rag = None
    try:
        if not os.getenv("OPENAI_API_KEY") and not API_KEY:
            raise ValueError("OPENAI_API_KEY or EMBEDDING_BINDING_API_KEY environment variable not set")
        rag = await initialize_rag()
        
        # Check which files are already indexed
        indexed_files = set()
        doc_status_file = os.path.join(WORKING_DIR, "kv_store_doc_status.json")
        if os.path.exists(doc_status_file):
            with open(doc_status_file, "r") as f:
                docs = json.load(f)
                indexed_files = {
                    doc["file_path"]
                    for doc in docs.values()
                    if doc.get("status") == "processed" and "file_path" in doc
                }
            print(f"Already indexed files: {indexed_files}")

        # Index new documents
        for doc_path in files_2b_indexed:
            if doc_path in indexed_files:
                print(f"Skipping already indexed file: {doc_path}")
                continue
            print(f"Checking document at: {doc_path}")
            if not os.path.exists(doc_path):
                print(f"Document file not found at: {doc_path}, skipping...")
                continue
            print(f"Indexing document: {doc_path}...")
            text_content = textract.process(doc_path, method="tesseract")
            decoded_text = text_content.decode('utf-8')
            decoded_text = re.sub(r"\n\s*\n", "\n", decoded_text)
            decoded_text = re.sub(r"Page \d+", "", decoded_text)
            print(f"Extracted text (first 100 chars): {decoded_text[:100]}")
            await rag.ainsert(decoded_text, ids=[os.path.basename(doc_path)], file_paths=os.path.basename(doc_path))
            print(f"Indexed {doc_path}")
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
    print("\nIndexing Done!")