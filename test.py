import json
# list(restaurantsInfo.values())[-remainingRestaurants:]



a = {"a": 1, "b": 8, "c": 3, "d": 4, "e": 5, "f": 0, "g": -1}
b = [4, 5, 6, 7, 8, 9, 10, 11, 12]
# a["a"] += b
index = 3
# print(a.values())
c = []
for b in list(a.values())[-index:]:
    c.append(b)

print(c)
# print(type(json.dumps(a)))