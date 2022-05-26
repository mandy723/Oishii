import json

a = {"a": [1, 2, 3]}
b = [4, 5, 6]
a["a"] += b

print(json.dumps(a))
print(type(json.dumps(a)))