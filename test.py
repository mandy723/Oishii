import json
# list(restaurantsInfo.values())[-remainingRestaurants:]

# sorted(restaurantsInfo.items(), key = lambda x: x[1])

a = {"r2": 1, "r1": 8, "r4": 3, "r3": 4, "r5": 5, "r8": 0, "r0": -1}
a = sorted(a.items(), key = lambda x: x[0])

print(a)
# b = [4, 5, 6, 7, 8, 9, 10, 11, 12]
# # a["a"] += b
# index = 3
# # print(a.values())
# c = [(1, 2, 3), ("a", "b", "c"), (5, 6, 7)]
# # for b in list(a.values())[-index:]:
# #     c.append(b)

# print(c[1][2])
# print(type(json.dumps(a)))