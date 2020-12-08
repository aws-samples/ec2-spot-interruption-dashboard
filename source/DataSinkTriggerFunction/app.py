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
from dynamodb_json import json_util as dynamodb_json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

data_sink_state_machine_arn = os.environ['DATA_SINK_STATE_MACHINE_ARN']

stepfunctions = boto3.client('stepfunctions')

def lambda_handler(event, context):

    logger.info(event)

    for record in event['Records']:
        if record['eventName'] == 'MODIFY':
            item = record['dynamodb']['NewImage']
            logger.info(item)

            if "InstanceMetadataEnriched" in item:
                if item['InstanceMetadataEnriched']['BOOL'] == True:

                    if item['LastEventType']['S'] == 'state-change' or item['LastEventType']['S'] == 'spot-interruption':
                        execution_input = {
                            'instance': dynamodb_json.loads(item)
                        }
                        
                        try:
                            logger.info('Attempting to Execute State Machine: {}'.format(data_sink_state_machine_arn))
                            response = stepfunctions.start_execution(
                                stateMachineArn=data_sink_state_machine_arn,
                                input=json.dumps(execution_input)
                                )
                            logger.info('Execution Response: {}'.format(response))
                        except Exception as e:
                            message = 'Error executing State Machine: {}'.format(e)
                            logger.info(message)
                            raise Exception(message)

    # End
    logger.info('Execution Complete')
    return