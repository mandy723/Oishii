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
import redis
import json
import configparser
import random
import requests
import time

app = Flask(__name__)

redisDB = redis.Redis(
    host='redis-18784.c299.asia-northeast1-1.gce.cloud.redislabs.com',
    port=18784, 
    password='YekHABXgrRh7pJdr1OvKbfXTyDtcphjD'
    )

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
        
    elif event.message.text == "I want more restaurants":
        remainingRestaurants, restaurants = prepareCarousel(event.source.user_id)
        columnAmount = 10 if remainingRestaurants >= 10 else remainingRestaurants

        if columnAmount:
            message = TemplateSendMessage(
                alt_text = "用屁電腦rrrrr",
                template = CarouselTemplate(columns = generate_carousel_columns(columnAmount, restaurants))
            )
            redisDB.hset(event.source.user_id, "remainingRestaurants", remainingRestaurants - columnAmount)
        
        else:
            message = TextSendMessage(text = "Please send location first")

        lineBotApi.reply_message(
            event.reply_token,
            message
            )
        
    elif event.message.text.lower() == "隨便吃":
        restaurant = json.loads(redisDB.hget(event.source.user_id, "r"+str(random.randint(1,10))).decode())
        message = generate_restaurant_button_message(restaurant)

        lineBotApi.reply_message(
            event.reply_token,
            message
        )

@handler.add(MessageEvent, message = LocationMessage)
def handle_location_message(event):
    lat = event.message.latitude
    long = event.message.longitude
    radius = 1500

    nearbyUrl = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={GOOGLE_API_KEY}&location={lat},{long}&radius={radius}&type=restaurant&language=zh-TW"

    results = requests.get(nearbyUrl).json()
    nearbyResults = results["results"]
    
    for i in range(2):  
        time.sleep(3)
        if "next_page_token" not in results:
            break
    
        nextPageToken = results['next_page_token'] 
        nextPageUrl = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={nextPageToken}&key={GOOGLE_API_KEY}&language=zh-TW"
        results = requests.get(nextPageUrl).json()
        nearbyResults += results["results"]
        
    for i in nearbyResults:
        if i.get("rating") is None:
            i["rating"] = 0.0
    nearbyResults.sort(key = lambda s: s["rating"], reverse=True)
    restaurants = {}
    restaurants["remainingRestaurants"] = len(nearbyResults)
    for i in range(len(nearbyResults)):
        restaurants["r"+str(i+1)] = json.dumps(nearbyResults[i])
    redisDB.hmset(event.source.user_id, restaurants)
    
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
    
    remainingRestaurants, restaurants = prepareCarousel(event.source.user_id)
    columnAmount = 10 if remainingRestaurants >= 10 else remainingRestaurants
    
    if columnAmount:
        message = TemplateSendMessage(
            alt_text = "用屁電腦rrrrr",
            template = CarouselTemplate(columns = generate_carousel_columns(columnAmount, restaurants))
        )
        redisDB.hset(event.source.user_id, "remainingRestaurants", remainingRestaurants - columnAmount)
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
    
def generate_carousel_columns(columnAmount, restaurants):
    carouselColumns = []
    
    for i in range(columnAmount):
        if restaurants[0].get("photos") is None:
            thumbnailImageUrl = None
        else:
            photoReference = restaurants[0]["photos"][0]["photo_reference"]
            thumbnailImageUrl = "https://maps.googleapis.com/maps/api/place/photo?key={}&photoreference={}&maxwidth=1024".format(GOOGLE_API_KEY, photoReference)
            
        rating = "無" if restaurants[0].get("rating") is None or restaurants[0]["rating"] == 0.0 else restaurants[0]["rating"]
        address = "沒有資料" if restaurants[0].get("vicinity") is None else restaurants[0]["vicinity"]
        
        userRatingsTotal = "0" if restaurants[0].get("user_ratings_total") is None else restaurants[0]["user_ratings_total"]
        column = CarouselColumn(
                    thumbnail_image_url = thumbnailImageUrl,
                    title = restaurants[0]["name"][:40],
                    text = f"評分：{rating}\n評論數：{userRatingsTotal}\n地址：{address}"[:60],
                    actions = [
                        URITemplateAction(
                            label = '查看地圖',
                            uri = "https://www.google.com/maps/search/?api=1&query={lat},{long}&query_place_id={placeId}".format(
                                lat = restaurants[0]["geometry"]["location"]["lat"],
                                long = restaurants[0]["geometry"]["location"]["lng"],
                                placeId = restaurants[0]["place_id"]
                            )
                        ),
                    ]
                )
        carouselColumns.append(column)

    return carouselColumns

def generate_restaurant_button_message(restaurant):
    if restaurant.get("photos") is None:
        thumbnailImageUrl = None
    else:
        photoReference = restaurant["photos"][0]["photo_reference"]
        thumbnailImageUrl = "https://maps.googleapis.com/maps/api/place/photo?key={}&photoreference={}&maxwidth=1024".format(GOOGLE_API_KEY, photoReference)
        
    rating = "無" if restaurant.get("rating") is None or restaurant["rating"] == 0.0 else restaurant["rating"]
    address = "沒有資料" if restaurant.get("vicinity") is None else restaurant["vicinity"]
    
    userRatingsTotal = "0" if restaurant.get("user_ratings_total") is None else restaurant["user_ratings_total"]

    buttons_template = TemplateSendMessage(
        alt_text = 'Please use mobile phone to check the message',
        template = ButtonsTemplate(
            title = restaurant["name"][:40],
            text = f"評分：{rating}\n評論數：{userRatingsTotal}\n地址：{address}"[:60],
            thumbnail_image_url = thumbnailImageUrl,
            actions = [
                URITemplateAction(
                    label = '查看地圖',
                    uri = "https://www.google.com/maps/search/?api=1&query={lat},{long}&query_place_id={placeId}".format(
                        lat = restaurant["geometry"]["location"]["lat"],
                        long = restaurant["geometry"]["location"]["lng"],
                        placeId = restaurant["place_id"]
                    )
                ),
            ]
        )
    )
    return buttons_template

def prepareCarousel(userId):
    restaurantsInfo = redisDB.hgetall(userId)
    print("infooooooooooooooooo", restaurantsInfo)
    remainingRestaurants = int(restaurantsInfo.pop("remainingRestaurants").decode())
    restaurants = []
    for r in list(restaurantsInfo.values())[-remainingRestaurants:]:
        restaurants.append(json.loads(r.decode()))
        
    return (remainingRestaurants, restaurants)

if __name__ == "__main__":
    app.run()