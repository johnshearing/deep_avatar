
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

def inspect_index():
    """Inspect the index to show document IDs and associated file paths."""
    doc_status_file = os.path.join(WORKING_DIR, "kv_store_doc_status.json")
    index_info = []
    if os.path.exists(doc_status_file):
        with open(doc_status_file, "r") as f:
            docs = json.load(f)
        for doc_id, doc_data in docs.items():
            # Check if the document is processed
            if doc_data.get("status") == "processed":
                # Get the file path, default to "Unknown"
                file_path = doc_data.get("file_path", "Unknown")
                # Initialize text snippet
                text_snippet = ""
                # Get the content field, which is a JSON string
                content_str = doc_data.get("content", "")
                if content_str:
                    try:
                        # Parse JSON string to dictionary
                        content_dict = json.loads(content_str)
                        # Extract first 100 chars of text
                        text_snippet = content_dict.get("text", "")[:100]
                        print(f"Debug: Parsed content for {doc_id}: {content_dict.get('text', '')[:200]}...")
                    except json.JSONDecodeError as e:
                        print(f"Debug: Failed to parse content for {doc_id}: {e}")
                        text_snippet = content_str[:100]
                index_info.append({"doc_id": doc_id, "file_path": file_path, "text_snippet": text_snippet})
        print("\nIndex Contents:")
        for info in index_info:
            print(f"Doc ID: {info['doc_id']}, File: {info['file_path']}, Text (first 100 chars): {info['text_snippet']}")
    else:
        print("Index file not found.")
    return index_info

async def main():
    """Main function to query the LightRAG index."""
    rag = None
    try:
        if not os.getenv("OPENAI_API_KEY") and not API_KEY:
            raise ValueError("OPENAI_API_KEY or EMBEDDING_BINDING_API_KEY environment variable not set")
        rag = await initialize_rag()
        
        # Check if index exists
        if not os.path.exists(os.path.join(WORKING_DIR, "kv_store_doc_status.json")):
            raise FileNotFoundError(f"No index found in {WORKING_DIR}. Run the indexing script first.")
        
        # Inspect index
        index_info = inspect_index()
        
        # Verify document ID
        target_doc_id = "doc-ff64a50cee496285dfdada9f69118734"
        doc_ids = get_indexed_doc_ids()
        if target_doc_id not in doc_ids:
            print(f"Warning: Document ID {target_doc_id} not found in index. Available IDs: {doc_ids}")
            return
        
        # Perform query
        query = (
            "Using only the text to answer, "
            "Tell us about the weather in Colorado. Please use only the provided text when forming your answer."
        )
        
        # Query in naive mode only, as it’s most likely to respect ids filter
        mode = "naive"
        print(f"\n=====================")
        print(f"Query mode: {mode}")
        print(f"=====================")
        try:
            response = await rag.aquery(
                query,
                param=QueryParam(mode=mode, top_k=50, ids=[target_doc_id])
            )
            logger.info(f"Raw response for mode {mode}: {response}")
            
            # Post-process response to ensure only target_doc_id is included
            filtered_response = response
            if isinstance(response, dict) and "chunks" in response:
                filtered_chunks = [
                    chunk for chunk in response["chunks"]
                    if chunk.get("doc_id") == target_doc_id
                ]
                filtered_response = {
                    **response,
                    "chunks": filtered_chunks,
                    "answer": f"Filtered to {target_doc_id}: {response.get('answer')}"
                }
            elif isinstance(response, str):
                filtered_response = f"Response (filtered to {target_doc_id}): {response}"
            
            print(f"Filtered Response:\n{filtered_response}")
            logger.info(f"Filtered response for mode {mode}: {filtered_response}")
        except Exception as e:
            logger.error(f"Error in mode {mode}: {str(e)}")
            print(f"Error in mode {mode}: {str(e)}")
    
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