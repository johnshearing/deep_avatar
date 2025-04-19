import numpy as np
from nano_vectordb.dbs import NanoVectorDB

vdb = NanoVectorDB(embedding_dim=1536, storage_file="test.json")

vdb.upsert([{
    "__id__": "test-id",
    "__vector__": np.zeros(1536),  # ← NumPy array instead of list
    "source": "unit test"
}])