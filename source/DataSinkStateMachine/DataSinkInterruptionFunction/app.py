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

from aws_embedded_metrics import metric_scope
from aws_embedded_metrics.config import get_config

Config = get_config()
Config.service_name = "EC2SpotInterruptions"
Config.service_type = "Instance"
Config.log_group_name = "EC2SpotInterruptions"

cloudwatch = boto3.client('cloudwatch')

@metric_scope
def put_instance_metric(instance, metrics):

    try:
        metrics.set_namespace("EC2SpotInterruptions")
        metrics.set_dimensions(
            { 
                "InstanceType": instance['InstanceType']
            })
        metrics.put_metric("Interruptions", 1, "Count")
        metrics.set_property("Region", instance['Region'])
        metrics.set_property("AvailabilityZone", instance['AvailabilityZone'])
        metrics.set_property("InstanceType", instance['InstanceType'])

        for tag in instance['Tags']:
            metrics.set_property(tag['Key'], tag['Value'])

    except ClientError as e:
        message = 'Error sending CloudWatch Metric: {}'.format(e)
        logger.info(message)
        raise Exception(message)
    
    return

@metric_scope
def put_availabilityzone_metric(instance, metrics):

    try:
        metrics.set_namespace("EC2SpotInterruptions")
        metrics.set_dimensions(
            { 
                "AvailabilityZone": instance['AvailabilityZone']
            })
        metrics.put_metric("Interruptions", 1, "Count")
        metrics.set_property("Region", instance['Region'])
        metrics.set_property("AvailabilityZone", instance['AvailabilityZone'])
        metrics.set_property("InstanceType", instance['InstanceType'])

        for tag in instance['Tags']:
            metrics.set_property(tag['Key'], tag['Value'])

    except ClientError as e:
        message = 'Error sending CloudWatch Metric: {}'.format(e)
        logger.info(message)
        raise Exception(message)

    return

def lambda_handler(event, context):

    logger.info(event)

    instance = event['instance']
    put_instance_metric(instance)
    put_availabilityzone_metric(instance)

    # End
    logger.info('Execution Complete')
    return