# Step 1
import requests
import json

LINE_CHANNEL_ACCESS_TOKEN = ''

Authorization_token = 'Bearer ' + LINE_CHANNEL_ACCESS_TOKEN

headers = {'Authorization': Authorization_token, 'Content-Type': 'application/json'}

body = {
    "size": {"width": 2500, "height": 834},
    "selected": "false",
    "name": "richmenu",
    "chatBarText": "Menu",
    "areas":[
        {
          "bounds": {"x": 0, "y": 0, "width": 834, "height": 834},
          "action": {"type": "message", "text": "Essential"}
        },
        {
          "bounds": {"x": 834, "y": 0, "width": 834, "height": 834},
          "action": {"type": "message", "text": "Thesaurus"}
        },
        {
          "bounds": {"x": 1666, "y": 0, "width": 834, "height": 834},
          "action": {"type": "message", "text": "Info."}
        }
    ]
  }

req = requests.request('POST', 'https://api.line.me/v2/bot/richmenu',
                       headers=headers, data=json.dumps(body).encode('utf-8'))
print(req.text) # record rich_menu_id
# ===========================================================================================
# Step 2
from linebot import (
    LineBotApi, WebhookHandler
)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
rich_menu_id = req.text[15:-2] # set rich_menu_id

path = "media/rich-menu.png" # local path

with open(path, 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, "image/png", f)

# ===========================================================================================
# Step 3
req = requests.request('POST', 'https://api.line.me/v2/bot/user/all/richmenu/'+rich_menu_id,
                       headers=headers)
print(req.text) # this will be {}

rich_menu_list = line_bot_api.get_rich_menu_list()
# ===========================================================================================
# Reset
# line_bot_api.delete_rich_menu(rich_menu_id)