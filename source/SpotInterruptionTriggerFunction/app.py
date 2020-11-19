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
import json
import logging

from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

instance_metadata_table = boto3.resource('dynamodb').Table(os.environ['INSTANCE_METADATA_TABLE'])

def lambda_handler(event, context):

    logger.info(event)

    # Transform CloudWatch Event
    item = {
        'InstanceId': event['detail']['instance-id'],
        'Region': event['region'],
        'LastEventTime': event['time'],
        'LastEventType': 'spot-interruption',
        'Interrupted': True,
        'InterruptedInstanceAction': event['detail']['instance-action'],
        'InterruptionTime': event['time']
    }

    logger.info(item)

    # Commit to DynamoDB
    try:
        response=instance_metadata_table.update_item(
            Key={
                'InstanceId': item['InstanceId']
            },
            UpdateExpression="SET #Region = :Region, #LastEventTime = :LastEventTime, #LastEventType = :LastEventType, #Interrupted = :Interrupted, #InterruptedInstanceAction = :InterruptedInstanceAction, #InterruptionTime = :InterruptionTime",
            ExpressionAttributeNames={
                '#Region' : 'Region',
                '#LastEventTime' : 'LastEventTime',
                '#LastEventType' : 'LastEventType',
                '#Interrupted' : 'Interrupted',
                '#InterruptedInstanceAction' : 'InterruptedInstanceAction',
                '#InterruptionTime' : 'InterruptionTime'
            },
            ExpressionAttributeValues={
                ':Region': item['Region'],
                ':LastEventTime': item['LastEventTime'],
                ':LastEventType': item['LastEventType'],
                ':Interrupted': item['Interrupted'],
                ':InterruptedInstanceAction': item['InterruptedInstanceAction'],
                ':InterruptionTime': item['InterruptionTime']
                },
            ReturnValues="NONE"
        )

        logger.info(response)
    except ClientError as e:
        message = 'Error updating instance in DynamoDB: {}'.format(e)
        logger.info(message)
        raise Exception(message)

    # End
    logger.info('Execution Complete')
    return