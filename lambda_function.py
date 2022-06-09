# Basic
import os
import json
from random import randint

# Line Bot SDK
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError 
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

# DynamoDB
import boto3
from boto3.dynamodb.conditions import Key

# Flex Msg Content
essential_msg_str = json.dumps(json.load(open('json/essential.json', 'r', encoding='utf-8')))
thesaurus_msg_str = json.dumps(json.load(open('json/thesaurus.json', 'r', encoding='utf-8')))
info_msg_str      = json.dumps(json.load(open('json/info.json', 'r', encoding='utf-8')))

import content.toefl as toefl
from make_msg import make_word_msg, set_progress

from datetime import datetime, timedelta
tz = timedelta(hours=8)

book2idx = {'Astronomy': 0, 'Archeology & Anthropology': 1, 'Art': 2, 'Biology & Botany': 3, 
            'Chemistry': 4, 'Earth Science': 5, 'Economics & Business': 6, 'Literature': 7, 
            'Medicine': 8, 'Physics': 9, 'Politics & Law': 10, 'Zoology': 11,
            'Essential200': 0, 'Essential500': 1}

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # Check if user exist, if not add user instance into DB
    dynamodb = boto3.resource('dynamodb') # connect to DynamoDB
    LineBotUser = dynamodb.Table('LineBotUser') # select table we will use after.
    
    user_id = event.source.user_id
    response = LineBotUser.get_item(Key={'LineID': user_id})
    state = ''
    if 'Item' in response:
        state = response['Item']['State']
    else:
        LineBotUser.put_item(Item={
            'LineID': user_id, 
            'State': 'Info.',
            'EssentialMsg': essential_msg_str,
            'EssentialClass': '',
            'Essential0': int(0),
            'Essential1': int(0),
            'ThesaurusMsg': thesaurus_msg_str,
            'ThesaurusClass': '',
            'Thesaurus0': int(0),
            'Thesaurus1': int(0),
            'Thesaurus2': int(0),
            'Thesaurus3': int(0),
            'Thesaurus4': int(0),
            'Thesaurus5': int(0),
            'Thesaurus6': int(0),
            'Thesaurus7': int(0),
            'Thesaurus8': int(0),
            'Thesaurus9': int(0),
            'Thesaurus10': int(0),
            'Thesaurus11': int(0)
        }) # insert data into DynamoDB

    # Check state
    item = response['Item']
    msg = event.message.text
    
    if msg in ('Essential', 'Thesaurus', 'Info.'):
        if msg == 'Essential':
            line_bot_api.reply_message(event.reply_token, 
                                       FlexSendMessage('essential', json.loads(item['EssentialMsg'])))
        elif msg == 'Thesaurus':
            line_bot_api.reply_message(event.reply_token, 
                                       FlexSendMessage('thesaurus', json.loads(item['ThesaurusMsg'])))
        elif msg == 'Info.':
            line_bot_api.reply_message(event.reply_token,
                                       FlexSendMessage('info', json.loads(info_msg_str)))
        LineBotUser.update_item(
            Key={'LineID': user_id}, 
            UpdateExpression="set #State=:newState",
            ExpressionAttributeNames={"#State": "State"},
            ExpressionAttributeValues={":newState": msg},
            ReturnValues="UPDATED_NEW"
        )
        return

    if state == 'Essential':
        book = item['EssentialClass']
        if msg in ('Essential200', 'Essential500'): book = msg
        elif msg != 'Next': return

        words = toefl.essential[book]
        n_words = len(words)
        offset = int(item['Essential'+str(book2idx[book])])

        response_msg = make_word_msg(words[offset])
        em = set_progress(item['EssentialMsg'], book2idx[book], int((offset/n_words)*100))

        LineBotUser.update_item(
            Key={'LineID': user_id}, 
            UpdateExpression="set #ec=:newEc, #progress=:newProgress, #em=:newEm",
            ExpressionAttributeNames={
                "#ec": "EssentialClass", 
                "#progress": "Essential"+str(book2idx[book]),
                "#em": "EssentialMsg"
            },
            ExpressionAttributeValues={
                ":newEc": book,
                ":newProgress": int((offset + 1) % n_words),
                ":newEm": json.dumps(em)
            },
            ReturnValues="UPDATED_NEW"
        )

        line_bot_api.reply_message(event.reply_token, 
                                   FlexSendMessage('word', response_msg))
        return

    if state == 'Thesaurus':
        book = item['ThesaurusClass']
        if msg in book2idx.keys(): book = msg
        elif msg != 'Next': return

        words = toefl.thesaurus[book]
        n_words = len(words)
        offset = int(item['Thesaurus'+str(book2idx[book])])

        response_msg = make_word_msg(words[offset])
        tm = set_progress(item['ThesaurusMsg'], book2idx[book], int((offset/n_words)*100))

        LineBotUser.update_item(
            Key={'LineID': user_id}, 
            UpdateExpression="set #tc=:newTc, #progress=:newProgress, #tm=:newTm",
            ExpressionAttributeNames={
                "#tc": "ThesaurusClass", 
                "#progress": "Thesaurus"+str(book2idx[book]),
                "#tm": "ThesaurusMsg"
            },
            ExpressionAttributeValues={
                ":newTc": book,
                ":newProgress": int((offset + 1) % n_words),
                ":newTm": json.dumps(tm)
            },
            ReturnValues="UPDATED_NEW"
        )

        line_bot_api.reply_message(event.reply_token, 
                                   FlexSendMessage('word', response_msg))
        return
        
def lambda_handler(event, context):
    # get X-Line-Signature header value
    signature = event['headers']['x-line-signature']

    # get request body as text
    body = event['body']

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return {
            'statusCode': 502,
            'body': json.dumps("Invalid signature. Please check your channel \
                                access token/channel secret.")
        }

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }