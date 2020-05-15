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

from botocore.exceptions import ClientError

instance_metadata_table = boto3.resource('dynamodb').Table(os.environ['INSTANCE_METADATA_TABLE'])

ec2 = boto3.client('ec2')

def paginate(method, **kwargs):
    client = method.__self__
    paginator = client.get_paginator(method.__name__)
    for page in paginator.paginate(**kwargs).result_key_iters():
        for item in page:
            yield item

def describe_instances(instance_ids):
    described_instances = []

    response = paginate(ec2.describe_instances, InstanceIds=instance_ids)

    print(response)

    for item in response:
        for instance in item['Instances']:
            described_instances.append(instance)

    return described_instances

def lambda_handler(event, context):

    print(event)

    instance_ids = []
    described_instances = []

    # Get Inserted Instances
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            item = record['dynamodb']['NewImage']
            instance_id = item['InstanceId']['S']
            instance_ids.append(instance_id)
            print(item)

    # Describe Instances
    if len(instance_ids) > 0:
        described_instances = describe_instances(instance_ids)
        print(described_instances)

    # Update Instance Records With Metadata

    for instance in described_instances:
        print(instance)
        try:

            item = {
                'InstanceId': instance['InstanceId'],
                'InstanceType': instance['InstanceType'],
                'InstanceLifecycle': '',
                'AvailabilityZone': instance['Placement']['AvailabilityZone'],
                'Tags': instance['Tags'],
                'InstanceMetadataEnriched': True
            }

            if 'InstanceLifecycle' in instance:
                item['InstanceLifecycle'] = instance['InstanceLifecycle']
            else:
                item['InstanceLifecycle'] = 'on-demand'

            response=instance_metadata_table.update_item(
                Key={
                    'InstanceId': item['InstanceId']
                },
                UpdateExpression="SET #InstanceType = :InstanceType, #InstanceLifecycle = :InstanceLifecycle, #AvailabilityZone = :AvailabilityZone, #Tags = :Tags, #InstanceMetadataEnriched = :InstanceMetadataEnriched",
                ExpressionAttributeNames={
                    '#InstanceType' : 'InstanceType',
                    '#InstanceLifecycle': 'InstanceLifecycle',
                    '#AvailabilityZone': 'AvailabilityZone',
                    '#Tags': 'Tags',
                    '#InstanceMetadataEnriched': 'InstanceMetadataEnriched'
                },
                ExpressionAttributeValues={
                    ':InstanceType': item['InstanceType'],
                    ':InstanceLifecycle': item['InstanceLifecycle'],
                    ':AvailabilityZone': item['AvailabilityZone'],
                    ':Tags': item['Tags'],
                    ':InstanceMetadataEnriched': item['InstanceMetadataEnriched']
                    },
                ReturnValues="NONE"
            )

            print(response)
        except ClientError as e:
            print(e)

    # End
    print('Execution Complete')
    return