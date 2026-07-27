from langgraph.checkpoint.memory import InMemorySaver
import inspect

print(inspect.signature(InMemorySaver.put))
print(inspect.signature(InMemorySaver.get_tuple))
print(inspect.signature(InMemorySaver.list))
print(inspect.signature(InMemorySaver.put_writes))