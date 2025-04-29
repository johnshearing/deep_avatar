import inspect
from tenacity import wait_exponential_jitter

print(f"Function: {wait_exponential_jitter}")
print()

print(f"Source File: {inspect.getfile(wait_exponential_jitter)}")
print()

print(f"Source Code:\n{inspect.getsource(wait_exponential_jitter)}")
print()