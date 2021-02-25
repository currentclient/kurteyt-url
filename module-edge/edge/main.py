"""
Lambda@edge

If not an api route, check url slug and redirect based on record in dynamodb
"""

import os

from edge import logger

LOGGER = logger.get_logger(__name__)

REGION = os.getenv("REGION")
ENVIRONMENT = os.getenv("ENVIRONMENT")


# Setup logger
LOGGER = logger.get_logger("index")


def handler(evt=None, ctx=None):  # pylint: disable=unused-argument
    """Handle for bus proccessor"""

    LOGGER.info(evt)

    try:
        #  Get the incoming request and the initial response from S3
        #  https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-event-structure.html
        cloudfront_details = evt["Records"][0]["cf"]

        LOGGER.info(cloudfront_details)
        LOGGER.info("Completed")

    except Exception as err:
        LOGGER.error("Failed with error: %s", err)
        raise err
