from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    LocationMessage,
    TemplateSendMessage,
    MessageTemplateAction,
    ButtonsTemplate,
    URITemplateAction,
    CarouselTemplate,
    CarouselColumn,
)
import configparser
import random
import requests


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GOOGLE_API_KEY = "AIzaSyABoNMQEdhfPSZexPLgkglXjXz6nRrqDxU"

nearbyResults = {}
# {"ID":"nearbyResults"}

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config.ini'))

lineBotApi = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

# 接收 LINE 的資訊
@app.route("/callback", methods = ['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text = True)
    app.logger.info("Request body: " + body)
    
    try:
        print(body, signature)
        handler.handle(body, signature)
        
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 學你說話
@handler.add(MessageEvent, message = TextMessage)
def pretty_echo(event):
    
    # if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        
    if event.message.text.lower() == "oishii":
        buttonsTemplateMessage = TemplateSendMessage(
        alt_text = "Please tell me where you are",
        template = ButtonsTemplate(
            text = "Please tell me where you are",
            actions = [
                URITemplateAction(
                    label = "Send my location",
                    uri = "line://nv/location"
                    )
                ]
            )
        )

        lineBotApi.reply_message(
            event.reply_token,
            buttonsTemplateMessage
            )
        
    elif event.message.text == "I want more restaurants":
        print("====================\n")
        print("In text message ->>>> " + str(event.source.user_id))
        print(nearbyResults)
        print("====================\n")
        
        restaurantsAmount = 10 if len(nearbyResults[event.source.user_id]) >= 10 else len(nearbyResults[event.source.user_id])
        if restaurantsAmount:
            message = TemplateSendMessage(
                alt_text = "用屁電腦rrrrr",
                template = CarouselTemplate(columns = generate_carousel_columns(restaurantsAmount, event.source.user_id))
            )
        else:
            message = TextSendMessage(text = "Please send location first")

        lineBotApi.reply_message(
            event.reply_token,
            message
            )
        
    # elif event.message.text.lower() == "隨便吃":

    #     lineBotApi.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text=pretty_text)
    #     )

@handler.add(MessageEvent, message = LocationMessage)
def handle_location_message(event):

    print("====================\n")
    print("In location message ->>>> " + str(event.source.user_id))
    print(nearbyResults)
    print("====================\n")

    lat = event.message.latitude
    long = event.message.longitude
    radius = 1500

    nearbyUrl = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={GOOGLE_API_KEY}&location={lat},{long}&radius={radius}&type=restaurant&language=zh-TW"

    results = requests.get(nearbyUrl).json()
    nearbyResults[event.source.user_id] = results["results"]
    
    for i in range(2):  
        if "next_page_token" not in results:
            break
    
        nextPageToken = results['next_page_token'] 
        nextPageUrl = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={nextPageToken}&key={GOOGLE_API_KEY}"
        results = requests.get(nextPageUrl).json()
        nearbyResults[event.source.user_id] += results["results"]

    nearbyResults[event.source.user_id].sort(key = lambda s: s["rating"], reverse=True)
    
    # restaurant = random.choice(nearbyResults)

    # 回覆使用 Buttons Template
    # buttons_template_message = TemplateSendMessage(
    # alt_text=restaurant["name"],
    # template=ButtonsTemplate(
    #         thumbnail_image_url=thumbnail_image_url,
    #         title=restaurant["name"],
    #         text=details,
    #         actions=[
    #             URITemplateAction(
    #                 label='查看地圖',
    #                 uri=map_url
    #             ),
    #         ]
    #     )
    # )

    restaurantsAmount = 10 if len(nearbyResults[event.source.user_id]) >= 10 else len(nearbyResults[event.source.user_id])

    if restaurantsAmount:
        message = TemplateSendMessage(
            alt_text = "用屁電腦rrrrr",
            template = CarouselTemplate(columns = generate_carousel_columns(restaurantsAmount, event.source.user_id))
        )
    else:
        message = TextSendMessage(text = "你家住海邊？")

    buttonsTemplateMessage = TemplateSendMessage(
        alt_text = "Wanna to see more?",
        template = ButtonsTemplate(
            text = "Wanna to see more?",
            actions = [
                MessageTemplateAction(
                    label= "Yes!",
                    text= "I want more restaurants"
                    )
                ]
            )
        )
    
    messageList = [message, buttonsTemplateMessage]
    
    lineBotApi.reply_message(
            event.reply_token, messageList
        )

# def generate_carousel_columns(restaurants, restaurantsAmount):
#     carouselColumns = []

#     for i in range(restaurantsAmount):
#         if restaurants[i].get("photos") is None:
#             thumbnailImageUrl = None
#         else:
#             photoReference = restaurants[i]["photos"][0]["photo_reference"]
#             thumbnailImageUrl = "https://maps.googleapis.com/maps/api/place/photo?key={}&photoreference={}&maxwidth=1024".format(GOOGLE_API_KEY, photoReference)
            
#         rating = "無" if restaurants[i].get("rating") is None else restaurants[i]["rating"]
#         address = "沒有資料" if restaurants[i].get("vicinity") is None else restaurants[i]["vicinity"]
#         userRatingsTotal = "0" if restaurants[i].get("user_ratings_total") is None else restaurants[i]["user_ratings_total"]
        
#         column = CarouselColumn(
#                     thumbnail_image_url = thumbnailImageUrl,
#                     title = restaurants[i]["name"][:40],
#                     text = "評分：{}\n評論數：{}\n地址：{}".format(rating, userRatingsTotal, address),
#                     actions = [
#                         URITemplateAction(
#                             label = '查看地圖',
#                             uri = "https://www.google.com/maps/search/?api=1&query={lat},{long}&query_place_id={placeId}".format(
#                                 lat = restaurants[i]["geometry"]["location"]["lat"],
#                                 long = restaurants[i]["geometry"]["location"]["lng"],
#                                 placeId = restaurants[i]["place_id"]
#                             )
#                         ),
#                     ]
#                 )
#         carouselColumns.append(column)

#     return carouselColumns
    
def generate_carousel_columns(restaurantsAmount, userId):
    carouselColumns = []
    print("=====\n")
    print(nearbyResults)
    print("\n=====")
    
    
    for i in range(restaurantsAmount):
        if nearbyResults[userId][0].get("photos") is None:
            thumbnailImageUrl = None
        else:
            photoReference = nearbyResults[userId][0]["photos"][0]["photo_reference"]
            thumbnailImageUrl = "https://maps.googleapis.com/maps/api/place/photo?key={}&photoreference={}&maxwidth=1024".format(GOOGLE_API_KEY, photoReference)
            
        rating = "無" if nearbyResults[userId][0].get("rating") is None else nearbyResults[userId][0]["rating"]
        address = "沒有資料" if nearbyResults[userId][0].get("vicinity") is None else nearbyResults[userId][0]["vicinity"]
        
        print("====================\n")
        print(str(i) + " ->>>> " + address)
        print("====================\n")
        
        userRatingsTotal = "0" if nearbyResults[userId][0].get("user_ratings_total") is None else nearbyResults[userId][0]["user_ratings_total"]
        
        column = CarouselColumn(
                    thumbnail_image_url = thumbnailImageUrl,
                    title = nearbyResults[userId][0]["name"][:40],
                    text = "評分：{}\n評論數：{}\n地址：{}".format(rating, userRatingsTotal, address),
                    actions = [
                        URITemplateAction(
                            label = '查看地圖',
                            uri = "https://www.google.com/maps/search/?api=1&query={lat},{long}&query_place_id={placeId}".format(
                                lat = nearbyResults[userId][0]["geometry"]["location"]["lat"],
                                long = nearbyResults[userId][0]["geometry"]["location"]["lng"],
                                placeId = nearbyResults[userId][0]["place_id"]
                            )
                        ),
                    ]
                )
        carouselColumns.append(column)
        nearbyResults[userId].pop(0)

    return carouselColumns

if __name__ == "__main__":
    app.run()