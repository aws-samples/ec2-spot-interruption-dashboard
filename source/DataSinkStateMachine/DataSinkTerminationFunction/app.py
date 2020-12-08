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

firehose = boto3.client('firehose')

instance_metadata_stream = os.environ['INSTANCE_METADATA_STREAM']

def sink_instance_data_to_firehose(instance):

    try:
        # Send Event to Firehose
        response = firehose.put_record(
            DeliveryStreamName=instance_metadata_stream,
            Record={
                'Data': json.dumps(instance)+"\n"
            }
        )
        logger.info(response)
        return instance

    except ClientError as e:
        message = 'Error sending instance data to Kinesis Firehose: {}'.format(e)
        logger.info(message)
        raise Exception(message)

    return

def lambda_handler(event, context):

    logger.info(event)

    instance = event['instance']
    sink_instance_data_to_firehose(instance)

    # End
    logger.info('Execution Complete')
    return