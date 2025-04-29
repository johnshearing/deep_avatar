from videorag import VideoRAG
import inspect

params = inspect.signature(VideoRAG.__init__).parameters
for name, param in params.items():
    print(f"{name}: default={param.default}, kind={param.kind}")