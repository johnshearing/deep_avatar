from videorag import QueryParam
import inspect

for name, param in inspect.signature(QueryParam.__init__).parameters.items():
    print(f"{name}: default={param.default}, kind={param.kind}")