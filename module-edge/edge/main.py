"""
Lambda@edge

If not an api route, check url slug and redirect based on record in dynamodb
"""

import boto3
from edge import logger

LOGGER = logger.get_logger(__name__)

# Setup boto3
SESSION = boto3.session.Session()
AWS_REGION = "us-east-1"

# Dyanmodb table name
KERTEYT_TABLE_NAME = "cc-east-dev-db-kurteyt"

# Lazy init cli
RES_CONTACT_TABLE = None


# Setup logger
LOGGER = logger.get_logger("index")


SUPPORTED_STATUS_CODES = {
    301: "Moved Permanently",
    302: "Found",
    307: "Temporary Redirect",
}

# Check its not an api route
def check_is_apiroute(path):
    """Check its an api route or a redirectable slug"""
    LOGGER.info(f"Checking is api route: {path}")
    is_apiroute = False

    if path.startswith("shorten"):
        is_apiroute = True

    return is_apiroute


def check_is_getmethod(method):
    """Check its a redirectable method"""
    LOGGER.info(f"Checking is get method: {method}")
    is_method = False

    if method == "GET":
        is_method = True

    return is_method


def get_redirect_record(slug):
    """Get redirect record from dynamodb"""

    LOGGER.info(f"Getting dynamod record with pk: {slug}")

    redirect_record = {}

    try:

        global RES_CONTACT_TABLE  # pylint: disable=global-statement

        if not RES_CONTACT_TABLE:
            RES_CONTACT_TABLE = SESSION.resource(
                service_name="dynamodb", region_name=AWS_REGION
            ).Table(KERTEYT_TABLE_NAME)

        get_response = RES_CONTACT_TABLE.get_item(
            Key={
                # PK and SK are on the record being passed in for updates
                "PK": slug,
            },
            ConsistentRead=False,  # True|False,
        )

        redirect_record = get_response.get("Item", False)

    except Exception as err:
        LOGGER.exception(err)

    return redirect_record


# Return redirect
def build_redirect(response, redirect_to_url, status_code=301):
    """Build the redirect response"""

    LOGGER.info(f"Build redirect to: {redirect_to_url}")

    # Note: We can't completely create a new set of headers even for a redirect
    # because Cloudfront fails painfully if you set (or clear) a "read-only" header.
    # https://github.com/awsdocs/amazon-cloudfront-developer-guide/blob/master/doc_source/lambda-requirements-limits.md#read-only-headers

    response["headers"]["location"] = [
        {
            "key": "Location",
            "value": redirect_to_url,
        }
    ]

    response["status"] = (status_code,)
    response["statusDescription"] = SUPPORTED_STATUS_CODES[status_code]

    return response


def make_response(cloudfront_event):
    """Check the request and determine response"""

    request = cloudfront_event["request"]
    response = cloudfront_event["response"]

    # Enable HSTS
    response["headers"]["strict-transport-security"] = [
        {"key": "Strict-Transport-Security", "value": "max-age=63072000"},
    ]

    # request.uri is just the URL path without hostname or querystring
    requested_path = request["uri"]
    # Remove leading slash
    requested_slug = requested_path[1:]
    requested_method = request["method"]

    # Return response and let it continue
    if check_is_apiroute(requested_slug):
        LOGGER.info("Forward to API")
        return response

    # If its not a GET method, dont redirect
    if not check_is_getmethod(requested_method):
        LOGGER.info("Forward to API, not a GET")
        return response

    # Read slug from dynamodb to get redirect path
    redirect_record = get_redirect_record(requested_slug)

    if not redirect_record:
        LOGGER.info("Forward to API, not a record")
        return response

    # Find target URL

    redirect_to_url = redirect_record.get("TargetUrl")
    LOGGER.info(f"Redirect to: {redirect_to_url}")

    response_with_redirect = build_redirect(response, redirect_to_url)

    return response_with_redirect


def handler(evt=None, ctx=None):
    """Handle viewer-request"""

    try:
        #  Get the incoming request and the initial response from S3
        #  https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-event-structure.html
        cloudfront_event = evt["Records"][0]["cf"]

        res = make_response(cloudfront_event)

        return res

    except Exception as err:
        LOGGER.error("Failed with error: %s", err)
        raise err
