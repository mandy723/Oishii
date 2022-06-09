import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage,
    LocationMessage,
)
from lineBotMessageBuilder import LineBotMessageBuilder
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
def handle_text_message(event):
    # if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
    
    messageBuilder = LineBotMessageBuilder()
    if event.message.text.lower() == "oishii":
        messageBuilder.start_building_template_message(alt_text="你在哪ㄦ")
        messageBuilder.add_button_template(text="你在哪ㄦ")
        messageBuilder.add_uri_template_action(label="傳送地址", uri="line://nv/location")
        message = messageBuilder.build()

        lineBotApi.reply_message(
            event.reply_token,
            message
        )

    elif event.message.text == "我要吃十家":
        if redisDB.exists(event.source.user_id):
            remainingRestaurants, restaurants = prepareCarousel(event.source.user_id)
            columnAmount = 10 if remainingRestaurants >= 10 else remainingRestaurants
            
            if columnAmount:
                redisDB.hset(event.source.user_id, "remainingRestaurants", remainingRestaurants - columnAmount)

                restaurantMessage = generate_restaurant_carousel_message(columnAmount, restaurants)

                messageBuilder.start_building_template_message(alt_text = "用屁電腦rrrrr")
                messageBuilder.add_button_template(text = "沒有你想吃的嗎？")
                messageBuilder.add_message_template_action(label = "看更多餐廳", text = "看更多餐廳")
                seeMoreRestaurantMessage = messageBuilder.build()
            
                messageList = [restaurantMessage, seeMoreRestaurantMessage]
                
                lineBotApi.reply_message(
                    event.reply_token, messageList
                )
        else:
            messageBuilder.start_building_template_message(alt_text = "用屁電腦rrrrr")
            messageBuilder.add_button_template(text = "你在哪？讓我看看！")
            messageBuilder.add_uri_template_action(label = "傳送地址", uri = "line://nv/location")
            message = messageBuilder.build()

            lineBotApi.reply_message(
                event.reply_token,
                message
            )
        
    elif event.message.text == "看更多餐廳":
        remainingRestaurants, restaurants = prepareCarousel(event.source.user_id)
        columnAmount = 10 if remainingRestaurants >= 10 else remainingRestaurants

        if columnAmount:
            redisDB.hset(event.source.user_id, "remainingRestaurants", remainingRestaurants - columnAmount)

            restaurantMessage = generate_restaurant_carousel_message(columnAmount, restaurants)
        
            messageBuilder.start_building_template_message(alt_text = "用屁電腦rrrrr")
            messageBuilder.add_button_template(text = "沒有你想吃的嗎？")
            messageBuilder.add_message_template_action(label = "看更多餐廳", text = "看更多餐廳")
            seeMoreRestaurantMessage = messageBuilder.build()

            messageList = [restaurantMessage, seeMoreRestaurantMessage]

            lineBotApi.reply_message(
                event.reply_token,
                messageList
            )
        else:
            messageBuilder.start_building_template_message(alt_text = "用屁電腦rrrrr")
            messageBuilder.add_button_template(text = "已經沒有更多餐廳了，還是不知道吃什麼嗎？")
            messageBuilder.add_message_template_action(label = "更新當前地址", text = "oishii")
            message = messageBuilder.build()

            lineBotApi.reply_message(
                event.reply_token,
                message
            )
        
    elif event.message.text.lower() == "隨便吃":
        if redisDB.exists(event.source.user_id):
            restaurant = json.loads(redisDB.hget(event.source.user_id, str(random.randint(1,10))).decode())
            message = generate_restaurant_button_message(restaurant)

            messageBuilder.start_building_template_message(alt_text = "用屁電腦rrrrr")
            messageBuilder.add_button_template(text = "還想怎麼吃？")
            messageBuilder.add_message_template_action(label = "隨便吃!", text = "隨便吃")
            messageBuilder.add_message_template_action(label = "我要吃十家!", text = "我要吃十家")
            messageBuilder.add_message_template_action(label = "更新當前地址", text = "oishii")
            optionsMessage = messageBuilder.build()

            messageList = [message, optionsMessage]

            lineBotApi.reply_message(
                event.reply_token,
                messageList
            )
        else:
            messageBuilder.start_building_template_message(alt_text = "用屁電腦rrrrr")
            messageBuilder.add_button_template(text = "你在哪？讓我看看！")
            messageBuilder.add_uri_template_action(label = "傳送地址", uri = "line://nv/location")
            message = messageBuilder.build()

            lineBotApi.reply_message(
                event.reply_token,
                message
            )

@handler.add(MessageEvent, message = LocationMessage)
def handle_location_message(event):
    lat = event.message.latitude
    long = event.message.longitude
    radius = 1500

    nearbyUrl = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={GOOGLE_API_KEY}&location={lat},{long}&radius={radius}&type=food&language=zh-TW"

    results = requests.get(nearbyUrl).json()
    nearbyResults = results["results"]
    messageBuilder = LineBotMessageBuilder()

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

        messageBuilder.start_building_template_message(alt_text = "用屁電腦rrrrr")
        messageBuilder.add_button_template(text = "想怎麼吃？")
        messageBuilder.add_message_template_action(label = "隨便吃!", text = "隨便吃")
        messageBuilder.add_message_template_action(label = "我要吃十家!", text = "我要吃十家")
        messageBuilder.add_message_template_action(label = "更新當前地址", text = "oishii")
        message = messageBuilder.build()

    else:
        messageBuilder.start_building_template_message(alt_text = "用屁電腦rrrrr")
        messageBuilder.add_button_template(text = "你家住海邊？")
        messageBuilder.add_message_template_action(label = "換個位置", text = "oishii")
        message = messageBuilder.build()

    lineBotApi.reply_message(
        event.reply_token,
        message
    )
    
def generate_restaurant_carousel_message(columnAmount, restaurants):
    messageBuilder = LineBotMessageBuilder()
    messageBuilder.start_building_template_message(alt_text = "用屁電腦rrrrr")
    messageBuilder.start_building_carousel_template()
    
    for i in range(columnAmount):
        if restaurants[i].get("photos") is None:
            thumbnailImageUrl = "https://img-prod-cms-rt-microsoft-com.akamaized.net/cms/api/am/imageFileData/RE4wpof?ver=d655"
        else:
            photoReference = restaurants[i]["photos"][0]["photo_reference"]
            thumbnailImageUrl = "https://maps.googleapis.com/maps/api/place/photo?key={}&photoreference={}&maxwidth=1024".format(GOOGLE_API_KEY, photoReference)
            
        rating = "無" if restaurants[i].get("rating") is None or restaurants[i]["rating"] == 0.0 else restaurants[i]["rating"]
        address = "沒有資料" if restaurants[i].get("vicinity") is None else restaurants[i]["vicinity"]
        
        userRatingsTotal = "0" if restaurants[i].get("user_ratings_total") is None else restaurants[i]["user_ratings_total"]

        messageBuilder.add_carousel_column(
            title = restaurants[i]["name"][:40],
            text = f"評分：{rating}\n評論數：{userRatingsTotal}\n地址：{address}"[:60],
            thumbnail_image_url = thumbnailImageUrl,
        )
        messageBuilder.add_uri_template_action(
            label = '查看地圖',
            uri = "https://www.google.com/maps/search/?api=1&query={lat},{long}&query_place_id={placeId}".format(
                lat = restaurants[i]["geometry"]["location"]["lat"],
                long = restaurants[i]["geometry"]["location"]["lng"],
                placeId = restaurants[i]["place_id"]
            )
        )

    messageBuilder.end_building_carousel_template()
    return messageBuilder.build()

def generate_restaurant_button_message(restaurant):
    if restaurant.get("photos") is None:
        thumbnailImageUrl = "https://img-prod-cms-rt-microsoft-com.akamaized.net/cms/api/am/imageFileData/RE4wpof?ver=d655"
    else:
        photoReference = restaurant["photos"][0]["photo_reference"]
        thumbnailImageUrl = "https://maps.googleapis.com/maps/api/place/photo?key={}&photoreference={}&maxwidth=1024".format(GOOGLE_API_KEY, photoReference)
    
    rating = "無" if restaurant.get("rating") is None or restaurant["rating"] == 0.0 else restaurant["rating"]
    address = "沒有資料" if restaurant.get("vicinity") is None else restaurant["vicinity"]
    
    userRatingsTotal = "0" if restaurant.get("user_ratings_total") is None else restaurant["user_ratings_total"]

    messageBuilder = LineBotMessageBuilder()
    messageBuilder.start_building_template_message("請使用手機版查看訊息呦～")
    messageBuilder.add_button_template(
        title = restaurant["name"][:40],
        text = f"評分：{rating}\n評論數：{userRatingsTotal}\n地址：{address}"[:60],
        thumbnail_image_url = thumbnailImageUrl
    )
    messageBuilder.add_uri_template_action(
        label = '查看地圖',
        uri = "https://www.google.com/maps/search/?api=1&query={lat},{long}&query_place_id={placeId}".format(
            lat = restaurant["geometry"]["location"]["lat"],
            long = restaurant["geometry"]["location"]["lng"],
            placeId = restaurant["place_id"]
        )
    )
    
    return messageBuilder.build()

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