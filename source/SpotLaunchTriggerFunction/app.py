 # Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 #
 # Permission is hereby granted, free of charge, to any person obtaining a copy of this
 # software and associated documentation files (the "Software"), to deal in the Software
 # without restriction, including without limitation the rights to use, copy, modify,
 # merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
 # permit persons to whom the Software is furnished to do so.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 # INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
 # PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 # HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 # OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 # SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import boto3
import os
import time

from botocore.exceptions import ClientError

instance_metadata_table = boto3.resource('dynamodb').Table(os.environ['INSTANCE_METADATA_TABLE'])
item_retention_days = os.environ['INSTANCE_METADATA_ITEM_RETENTION_DAYS']
item_expiration_days = int(item_retention_days)*60*60*24

def lambda_handler(event, context):

    print(event)

    # Transform CloudWatch Event
    item = {
        'InstanceId': event['detail']['instance-id'],
        'Region': event['region'],
        'LastEventTime': event['time'],
        'LastEventType': 'spot-launch',
        'SpotInstanceRequestId': event['detail']['spot-instance-request-id'],
        'ExpirationTime': int(time.time() + item_expiration_days)
    }

    print(item)
    
    # Commit to DynamoDB
    try:

        response=instance_metadata_table.update_item(
            Key={
                'InstanceId': item['InstanceId']
                },
            UpdateExpression="SET #Region = :Region, #LastEventTime = :LastEventTime, #LastEventType = :LastEventType, #SpotInstanceRequestId = :SpotInstanceRequestId, #ExpirationTime = :ExpirationTime",
            ExpressionAttributeNames={
                '#Region' : 'Region',
                '#LastEventTime' : 'LastEventTime',
                '#LastEventType' : 'LastEventType',
                '#SpotInstanceRequestId' : 'SpotInstanceRequestId',
                '#ExpirationTime': 'ExpirationTime'
            },            
            ExpressionAttributeValues={
                ':Region': item['Region'],
                ':LastEventTime': item['LastEventTime'],
                ':LastEventType': item['LastEventType'],
                ':SpotInstanceRequestId': item['SpotInstanceRequestId'],
                ':ExpirationTime': 'ExpirationTime'                  
                },
            ReturnValues="NONE"
        )

        print(response)
    except ClientError as e:
        print(e)

    # End
    print('Execution Complete')
    return