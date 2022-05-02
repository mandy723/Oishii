from __future__ import unicode_literals
import os
import json
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    LocationMessage,
    TemplateSendMessage, ButtonsTemplate, URITemplateAction,
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

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))


# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        print(body, signature)
        handler.handle(body, signature)
        
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 學你說話
@handler.add(MessageEvent, message=TextMessage)
def pretty_echo(event):
    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        
        # Phoebe 愛唱歌
        pretty_note = '♫♪♬'
        pretty_text = ''
        
        for i in event.message.text:
        
            pretty_text += i
            pretty_text += random.choice(pretty_note)

        if event.message.text.lower() == "oishii":
            buttons_template_message = TemplateSendMessage(
            alt_text="Please tell me where you are",
            template=ButtonsTemplate(
                text="Please tell me where you are",
                actions=[
                    URITemplateAction(
                        label="Send my location",
                        uri="line://nv/location"
                        )
                    ]
                )
            )

            line_bot_api.reply_message(
                event.reply_token,
                buttons_template_message
                )

        elif event.message.text.lower() == "隨便吃":
    
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=pretty_text)
            )

        else:
            text=f'event.reply_token: {event.reply_token}\n' + 'event.source.user_id: {event.source.user_id}' + 'event.message.text: {event.message.text}'

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=text)
            )

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    # 獲取使用者的經緯度
    lat = event.message.latitude
    long = event.message.longitude

    # 使用 Google API Start =========
    # 1. 搜尋附近餐廳
    nearby_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={}&location={},{}&rankby=distance&type=restaurant&language=zh-TW".format(GOOGLE_API_KEY, lat, long)
    nearby_results = requests.get(nearby_url)

    # 隨機選擇一間餐廳
    nearby_restaurants_dict = nearby_results.json()
    top20_restaurants = nearby_restaurants_dict["results"]
    restaurant = random.choice(top20_restaurants)

    # 4. 檢查餐廳有沒有照片，有的話會顯示
    if restaurant.get("photos") is None:
        thumbnail_image_url = None
    else:
        # 根據文件，最多只會有一張照片
        photo_reference = restaurant["photos"][0]["photo_reference"]
        thumbnail_image_url = "https://maps.googleapis.com/maps/api/place/photo?key={}&photoreference={}&maxwidth=1024".format(GOOGLE_API_KEY, photo_reference)
    # 5. 組裝餐廳詳細資訊
    rating = "無" if restaurant.get("rating") is None else restaurant["rating"]
    address = "沒有資料" if restaurant.get("vicinity") is None else restaurant["vicinity"]
    details = "評分：{}\n地址：{}".format(rating, address)

    # 6. 取得餐廳的 Google map 網址
    map_url = "https://www.google.com/maps/search/?api=1&query={lat},{long}&query_place_id={place_id}".format(
        lat=restaurant["geometry"]["location"]["lat"],
        long=restaurant["geometry"]["location"]["lng"],
        place_id=restaurant["place_id"]
    )
    # 使用 Google API End =========

    # 回覆使用 Buttons Template
    buttons_template_message = TemplateSendMessage(
    alt_text=restaurant["name"],
    template=ButtonsTemplate(
            thumbnail_image_url=thumbnail_image_url,
            title=restaurant["name"],
            text=details,
            actions=[
                URITemplateAction(
                    label='查看地圖',
                    uri=map_url
                ),
            ]
        )
    )

    line_bot_api.reply_message(
            event.reply_token,
            buttons_template_message
        )

if __name__ == "__main__":
    app.run()