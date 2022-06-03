import json

a = {"a": {"aa":"11"}}
b = [4, 5, 6]
# a["a"] += b

# print(a.values())

print(json.dumps(a))
# print(type(json.dumps(a)))