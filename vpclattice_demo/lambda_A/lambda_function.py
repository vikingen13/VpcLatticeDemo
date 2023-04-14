# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#lambda handler
def lambda_handler(event, context):

    return {
            'statusCode': 200,
            'body': 'Hello from Lambda!\n'
        }