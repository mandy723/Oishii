from linebot import  LineBotApi
import configparser
import requests
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config.ini'))

lineBotApi = LineBotApi(config.get('line-bot', 'channel_access_token'))

headers = {'Authorization':f'Bearer {config.get("line-bot", "channel_access_token")}','Content-Type':'application/json'}

body = {
    'size': {'width': 2500, 'height': 640},    # 設定尺寸
    'selected': 'true',                        # 預設是否顯示
    'name': 'menu',                            # 選單名稱
    'chatBarText': 'menu',                     # 選單在 LINE 顯示的標題
    'areas':[                                  # 選單內容
        {
          'bounds': {'x': 0, 'y': 0, 'width': 625, 'height': 640},           # 選單位置與大小
          'action': {'type': 'uri', 'uri': 'https://line.me/R/nv/location/'}  # 點擊後開啟地圖定位，傳送位置資訊
        },
        {
          'bounds': {'x': 626, 'y': 0, 'width': 625, 'height': 640},
          'action': {'type': 'message', 'text': '搜尋關鍵字'} 
        },
        {
          'bounds': {'x': 1251, 'y': 0, 'width':625, 'height': 640},     # 選單位置與大小
          'action': {'type': 'message', 'text':'隨便吃'}               # 點擊後傳送文字
        },
        {
          'bounds': {'x': 1879, 'y': 0, 'width':625, 'height': 640},     # 選單位置與大小
          'action': {'type': 'message', 'text':'我要吃十家'}               # 點擊後傳送文字
        }
    ]
  }

class LineBotRichMenu():

  def create_rich_menu(self):
    # 向指定網址發送 request
    req = requests.request('POST', 'https://api.line.me/v2/bot/richmenu',
                          headers=headers,data=json.dumps(body).encode('utf-8'))
    # 印出得到的結果
    print(req.text)
    return json.loads(req.text).get("richMenuId")

  def set_picture_of_rich_menu(self, richMenuId):
    # 設定 menu 圖片
    with open("line-bot-menu.jpeg", 'rb') as f:
        lineBotApi.set_rich_menu_image(richMenuId, "image/jpeg", f)

  def activate_rich_menu(self, richMenuId):
    req = requests.request('POST', f'https://api.line.me/v2/bot/user/all/richmenu/{richMenuId}', 
                          headers=headers)

    print(req.text)

  def get_rich_menu_list(self):
    rich_menu_list = lineBotApi.get_rich_menu_list()
    for rich_menu in rich_menu_list:
        print(rich_menu.rich_menu_id)

    return rich_menu_list

  def delete_rich_menu(self, richMenuId):
    lineBotApi.delete_rich_menu(richMenuId)

if __name__ == "__main__":
    menu = LineBotRichMenu()

    richMenuId = menu.create_rich_menu()
    menu.set_picture_of_rich_menu(richMenuId)
    menu.activate_rich_menu(richMenuId)
    # richMenuId = "richmenu-fdceb72059bc1f37e03e49c46b22bd1a"
    # menu.delete_rich_menu(richMenuId)
