# LINE Bot - Vocabulary Learning Assistant

## [Line Bot]((https://github.com/line/line-bot-sdk-python))
- Register a [LINE Developer](https://developers.line.biz/console/) account
- Create New Provider
- Messaging API > Create Channel
	- Remember your Channel secret & Channel access token
	- Auto-reply messages: Disabled
	- Scan your QR code to add your LINE Bot as a friend
- Install and zip the package on your local PC for creating layer(s) in AWS Lambda
  ```
  $ pip install line-bot-sdk -t python/
  $ zip -r linebot_layer.zip python/
  ```
- Run set_richmenu.py on your local PC
  `$ python set_richmenu.py`


## AWS Lambda
- Layers > Create layer
	- Name
	  linebot-layer
    - Upload a .zip file
    - Runtimes
      Python 3.7, Python 3.8, Python 3.9
- Function > Create function
	- Name
	  LineBot
	- Runtime
	  Python 3.9
- LineBot (in your function)
	- Layers > Add a layer > Custom layers > Choose "linebot-layer"
	- Configuration > Environment variables
		- CHANNEL_ACCESS_TOKEN : \<your_channel_access_token\>
		- CHANNEL_SECRET : \<your_channel_secret\>
	- Paste the codes & Deploy
	- Configuration > Permissions > Execution role
	    - Click the role and it will navigate to AWS IAM console.
	    - Add permissions > Attach policies
	      Add AmazonDynamoDBFullAccess
	- If you want to monitor your logs 
	  Monitor > View logs in CloudWatch

## AWS API Gateway
- APIs > Create API > REST API / Build
    - API name
      LineBotWebhook
    - Create API
- LineBotWebhook (in your API)
    - Actions > Create Method > POST (checked)
	    - Integration type
	      Lambda Function
	    - Use Lambda Proxy Integration (checked)
	    - Lambda Region
	      us-east-1 (all the regions in AWS services should be the same)
	    - Lambda Function
	      LineBot
	    - Use Default Timeout (checked)
	    - Save
	- Actions > Deploy API
	    - Stage name
	      prod
	    - Deploy
	- Stages
	  Invoke URL: https://.....us-east-1.amazonaws.com/prod
	  (Copy & Paste to Webhook URL in LINE Developer > your LINE Bot > Messaging API)

## AWS DynamoDB
- Tables > Create table
	- Table name
	  LineBotUser
	- Partition key
	  LineID
	- Sort key (optional)
	  If you set this, you need to include it in get_item, delete_item, etc.