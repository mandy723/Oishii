import json
from lineBotMessageBuilder import LineBotMessageBuilder
# list(restaurantsInfo.values())[-remainingRestaurants:]

# sorted(restaurantsInfo.items(), key = lambda x: x[1])

# a = {"r2": 1, "r1": 8, "r4": 3, "r35": 4, "r3": 5, "r8": 0, "r10": -1}
# a = sorted(a.items(), key = lambda x: x[0])
# a = ["123", "456"]
# print(type(a) == list)

# messageBuilder = LineBotMessageBuilder()

# messageBuilder.start_building_template_message(alt_text="test")
# messageBuilder.start_building_carousel_template()
# messageBuilder.add_carousel_column(text="text")
# messageBuilder.add_message_template_action("label", "text")
# messageBuilder.add_carousel_column(text = "text1")
# messageBuilder.add_url_template_action("label1", "https://123.com")
# messageBuilder.end_building_carousel_template()
# message = messageBuilder.build()
# print(message)

# b = [4, 5, 6, 7, 8, 9, 10, 11, 12]
# # a["a"] += b
# index = 3
# # print(a.values())
# c = [(1, 2, 3), ("a", "b", "c"), (5, 6, 7)]
# # for b in list(a.values())[-index:]:
# #     c.append(b)

# print(c[1][2])
# print(type(json.dumps(a)))