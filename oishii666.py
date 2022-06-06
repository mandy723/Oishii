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

@handler.add(MessageEvent, message = TextMessage)
def pretty_echo(event):
    
    # if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        
    if event.message.text.lower() == "oishii":
        buttonsTemplateMessage = TemplateSendMessage(
        alt_text = "你在哪ㄦ",
        template = ButtonsTemplate(
            text = "你在哪ㄦ",
            actions = [
                URITemplateAction(
                    label = "傳送地址",
                    uri = "line://nv/location"
                    )
                ]
            )
        )

        lineBotApi.reply_message(
            event.reply_token,
            buttonsTemplateMessage
        )

    elif event.message.text == "我要吃十家":
        if redisDB.exists(event.source.user_id):
            remainingRestaurants, restaurants = prepareCarousel(event.source.user_id)
            columnAmount = 10 if remainingRestaurants >= 10 else remainingRestaurants
            
            if columnAmount:
                message = TemplateSendMessage(
                    alt_text = "用屁電腦rrrrr",
                    template = CarouselTemplate(columns = generate_carousel_columns(columnAmount, restaurants))
                )
                redisDB.hset(event.source.user_id, "remainingRestaurants", remainingRestaurants - columnAmount)

                buttonsTemplateMessage = TemplateSendMessage(
                alt_text = "用屁電腦rrrrr",
                template = ButtonsTemplate(
                    text = "沒有你想吃的嗎？",
                    actions = [
                        MessageTemplateAction(
                            label= "看更多餐廳",
                            text= "看更多餐廳"
                            )
                        ]
                    )
                )
            
                messageList = [message, buttonsTemplateMessage]
                
                lineBotApi.reply_message(
                    event.reply_token, messageList
                )
        else:
            message = TemplateSendMessage(
                alt_text = "用屁電腦rrrrr",
                template = ButtonsTemplate(
                    text = "你在哪？讓我看看！",
                    actions = [
                        MessageTemplateAction(
                            label= "更新當前地址",
                            text= "oishii"
                        ),
                    ]
                )
            )

            lineBotApi.reply_message(
                event.reply_token,
                message
            )
        
    elif event.message.text == "看更多餐廳":
        remainingRestaurants, restaurants = prepareCarousel(event.source.user_id)
        columnAmount = 10 if remainingRestaurants >= 10 else remainingRestaurants

        if columnAmount:
            message = TemplateSendMessage(
                alt_text = "用屁電腦rrrrr",
                template = CarouselTemplate(columns = generate_carousel_columns(columnAmount, restaurants))
            )
            redisDB.hset(event.source.user_id, "remainingRestaurants", remainingRestaurants - columnAmount)
        
            buttonsTemplateMessage = TemplateSendMessage(
                alt_text = "用屁電腦rrrrr",
                template = ButtonsTemplate(
                    text = "沒有你想吃的嗎？",
                    actions = [
                        MessageTemplateAction(
                            label= "看更多餐廳",
                            text= "看更多餐廳"
                        )
                    ]
                )
            )

            messageList = [message, buttonsTemplateMessage]

            lineBotApi.reply_message(
                event.reply_token,
                messageList
            )
        else:
            message = TemplateSendMessage(
                alt_text = "用屁電腦rrrrr",
                template = ButtonsTemplate(
                    text = "已經沒有更多餐廳了，還是不知道吃什麼嗎？",
                    actions = [
                        MessageTemplateAction(
                            label= "更新當前地址",
                            text= "oishii"
                        ),
                    ]
                )
            )

            lineBotApi.reply_message(
                event.reply_token,
                message
            )
        
    elif event.message.text.lower() == "隨便吃":
        if redisDB.exists(event.source.user_id):
            restaurant = json.loads(redisDB.hget(event.source.user_id, str(random.randint(1,10))).decode())
            message = generate_restaurant_button_message(restaurant)

            optionsMessage = TemplateSendMessage(
                alt_text = "用屁電腦rrrrr",
                template = ButtonsTemplate(
                    text = "還想怎麼吃？",
                    actions = [
                        MessageTemplateAction(
                            label= "隨便吃!",
                            text= "隨便吃"
                        ),
                        MessageTemplateAction(
                            label= "我要吃十家!",
                            text= "我要吃十家"
                        ),
                        MessageTemplateAction(
                            label= "更新當前地址",
                            text= "oishii"
                        )
                    ]
                )
            )

            messageList = [message, optionsMessage]

            lineBotApi.reply_message(
                event.reply_token,
                messageList
            )
        else:
            message = TemplateSendMessage(
                alt_text = "用屁電腦rrrrr",
                template = ButtonsTemplate(
                    text = "你在哪？讓我看看！",
                    actions = [
                        MessageTemplateAction(
                            label= "更新當前地址",
                            text= "oishii"
                        ),
                    ]
                )
            )

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

    if nearbyResults:
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
            restaurants[str(i+1)] = json.dumps(nearbyResults[i])
        redisDB.hmset(event.source.user_id, restaurants)

        optionsMessage = TemplateSendMessage(
            alt_text = "用屁電腦rrrrr",
            template = ButtonsTemplate(
                text = "想怎麼吃？",
                actions = [
                    MessageTemplateAction(
                        label= "隨便吃!",
                        text= "隨便吃"
                    ),
                    MessageTemplateAction(
                        label= "我要吃十家!",
                        text= "我要吃十家"
                    ),
                    MessageTemplateAction(
                        label= "更新當前地址",
                        text= "oishii"
                    )
                ]
            )
        )

    else:
        optionsMessage = TemplateSendMessage(
            alt_text = "用屁電腦rrrrr",
            template = ButtonsTemplate(
                text = "你家住海邊？",
                actions = [
                    MessageTemplateAction(
                        label= "換個位置",
                        text= "oishii"
                    ),
                ]
            )
        )

    lineBotApi.reply_message(
        event.reply_token,
        optionsMessage
    )
    
def generate_carousel_columns(columnAmount, restaurants):
    carouselColumns = []
    
    for i in range(columnAmount):
        if restaurants[i].get("photos") is None:
            thumbnailImageUrl = None
        else:
            photoReference = restaurants[i]["photos"][0]["photo_reference"]
            thumbnailImageUrl = "https://maps.googleapis.com/maps/api/place/photo?key={}&photoreference={}&maxwidth=1024".format(GOOGLE_API_KEY, photoReference)
            
        rating = "無" if restaurants[i].get("rating") is None or restaurants[i]["rating"] == 0.0 else restaurants[i]["rating"]
        address = "沒有資料" if restaurants[i].get("vicinity") is None else restaurants[i]["vicinity"]
        
        userRatingsTotal = "0" if restaurants[i].get("user_ratings_total") is None else restaurants[i]["user_ratings_total"]
        column = CarouselColumn(
                    thumbnail_image_url = thumbnailImageUrl,
                    title = restaurants[i]["name"][:40],
                    text = f"評分：{rating}\n評論數：{userRatingsTotal}\n地址：{address}"[:60],
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
    restaurantsInfo = { key.decode(): val.decode() for key, val in redisDB.hgetall(userId).items() }
    remainingRestaurants = int(restaurantsInfo.pop(("remainingRestaurants")))
    restaurants = []
    
    sortedRestaurants = sorted(restaurantsInfo.items(), key = lambda x: int(x[0]))

    for r in sortedRestaurants[-remainingRestaurants:]:
        restaurants.append(json.loads(r[1]))
        
    return (remainingRestaurants, restaurants)

if __name__ == "__main__":
    app.run()