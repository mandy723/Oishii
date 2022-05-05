from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    LocationMessage,
    TemplateSendMessage,
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

    # elif event.message.text.lower() == "隨便吃":

    #     lineBotApi.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text=pretty_text)
    #     )

@handler.add(MessageEvent, message = LocationMessage)
def handle_location_message(event):
    lat = event.message.latitude
    long = event.message.longitude

    nearbyUrl = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={}&location={},{}&radius={}&type=restaurant&language=zh-TW".format(GOOGLE_API_KEY, lat, long, 1500)

    nearbyResults = requests.get(nearbyUrl)
    
    # next_page_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={}&key={}}".format(nearby_results.json()["next_page_token"], GOOGLE_API_KEY)

    nearbyRestaurantsDict = nearbyResults.json()
    top20Restaurants = nearbyRestaurantsDict["results"]
    # restaurant = random.choice(top20Restaurants)

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

    restaurantsAmount = 10 if len(top20Restaurants) >= 10 else len(top20Restaurants)

    if restaurantsAmount:
        message = TemplateSendMessage(
            alt_text = "用屁電腦rrrrr",
            template = CarouselTemplate(columns = generate_carousel_columns(top20Restaurants, restaurantsAmount))
        )
    else:
        message = TextSendMessage(text = "你家住海邊？")

    lineBotApi.reply_message(
            event.reply_token,
            message
        )

def generate_carousel_columns(restaurants, restaurantsAmount):
    carouselColumns = []

    for i in range(restaurantsAmount):
        if restaurants[i].get("photos") is None:
            thumbnailImageUrl = None
        else:
            photoReference = restaurants[i]["photos"][0]["photo_reference"]
            thumbnailImageUrl = "https://maps.googleapis.com/maps/api/place/photo?key={}&photoreference={}&maxwidth=1024".format(GOOGLE_API_KEY, photoReference)
            
        rating = "無" if restaurants[i].get("rating") is None else restaurants[i]["rating"]
        address = "沒有資料" if restaurants[i].get("vicinity") is None else restaurants[i]["vicinity"]
        userRatingsTotal = "0" if restaurants[i].get("user_ratings_total") is None else restaurants[i]["user_ratings_total"]
        
        column = CarouselColumn(
                    thumbnail_image_url = thumbnailImageUrl,
                    title = restaurants[i]["name"][:40],
                    text = "評分：{}\n評論數：{}\n地址：{}".format(rating, userRatingsTotal, address),
                    actions = [
                        URITemplateAction(
                            label = '查看地圖',
                            uri = "https://www.google.com/maps/search/?api=1&query={lat},{long}&query_place_id={placeId}".format(
                                lat = restaurants[i]["geometry"]["location"]["lat"],
                                long = restaurants[i]["geometry"]["location"]["lng"],
                                placeId = restaurants[i]["place_id"]
                            )
                        ),
                    ]
                )
        carouselColumns.append(column)

    return carouselColumns
    

if __name__ == "__main__":
    app.run()