# Used to test document ids filtering function. Turns out that filtering does not work and it is a known bug. 

import os
import asyncio
import logging
import logging.config
import json
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import logger, set_verbose_debug, EmbeddingFunc
from llama_index.embeddings.openai import OpenAIEmbedding

# Configuration
WORKING_DIR = "_charles_work_dir"
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

def get_indexed_doc_ids():
    """Retrieve all document IDs from the index."""
    doc_status_file = os.path.join(WORKING_DIR, "kv_store_doc_status.json")
    doc_ids = []
    if os.path.exists(doc_status_file):
        with open(doc_status_file, "r") as f:
            docs = json.load(f)
            doc_ids = [doc_id for doc_id, doc in docs.items() if doc.get("status") == "processed"]
        print(f"Indexed document IDs: {doc_ids}")
    else:
        print("No document status file found.")
    return doc_ids

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
        
        # Verify document ID
        target_doc_id = "doc-c933966c02ad9fa200190ef53f843b0e"
        doc_ids = get_indexed_doc_ids()
        if target_doc_id not in doc_ids:
            print(f"Warning: Document ID {target_doc_id} not found in index. Available IDs: {doc_ids}")
        
        # Perform query
        query = (
            "Using only the text to answer, "
            "Tell us about the weather in Colorado. "
            "Please use only the provided text when forming your answer."
        )
        
        # Query modes, excluding 'hybrid' due to context processing issue
        modes = ["naive", "local", "global", "mix"]  # Removed 'hybrid'
        for mode in modes:
            print(f"\n=====================")
            print(f"Query mode: {mode}")
            print(f"=====================")
            try:
                response = await rag.aquery(
                    query,
                    param=QueryParam(mode=mode, top_k=50, ids=[target_doc_id])
                )
                logger.info(f"Response for mode {mode}: {response}")
                print(response)
            except Exception as e:
                logger.error(f"Error in mode {mode}: {str(e)}")
                print(f"Error in mode {mode}: {str(e)}")
        
        # Optional: Try hybrid mode separately with extra error handling
        mode = "hybrid"
        print(f"\n=====================")
        print(f"Query mode: {mode}")
        print(f"=====================")
        try:
            response = await rag.aquery(
                query,
                param=QueryParam(mode=mode, top_k=50, ids=[target_doc_id])
            )
            logger.info(f"Response for mode {mode}: {response}")
            print(response)
        except Exception as e:
            logger.error(f"Error in hybrid mode: {str(e)}")
            print(f"Error in hybrid mode: {str(e)}")
            print("Note: Hybrid mode may have issues with the 'ids' filter. Consider using other modes.")
    
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