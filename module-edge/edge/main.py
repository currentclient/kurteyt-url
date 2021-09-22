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
KERTEYT_TABLE_NAME = None
EXPIRED_REDIRECT = None

# Lazy init cli
RES_CONTACT_TABLE = None

# Setup logger
LOGGER = logger.get_logger("index")


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <!-- OG settings -->
    <meta property="og:title" content="$OG_TITLE" />
    <meta property="og:description" content="$OG_DESCRIPTION" />
    <meta property="og:url" content="$OG_URL" />
    <meta property="og:image" content="$OG_IMAGE" />
    <meta property="og:image:alt" content="$OG_IMAGE_ALT" />
    <meta property="og:type" content="website" />
    <title>CurrentClient</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap"
      rel="stylesheet"
    />

    <link
      href="https://fonts.googleapis.com/css2?family=Caveat&display=swap"
      rel="stylesheet"
    />

    <script>
      window.onload = function () {
        // similar behavior as clicking on a link
        setTimeout(() => {
          window.location.href = "$REDIRECT_URL";
        }, 3000);
      };
    </script>
    <style>
      /* RESET */
      /* Box sizing rules */
      *,
      *::before,
      *::after {
        box-sizing: border-box;
      }

      /* Remove default margin */
      body,
      h1,
      h2,
      h3,
      h4,
      p,
      figure,
      blockquote,
      dl,
      dd {
        margin: 0;
      }

      /* Remove list styles on ul, ol elements with a list role, which suggests default styling will be removed */
      ul[role="list"],
      ol[role="list"] {
        list-style: none;
      }

      /* Set core root defaults */
      html:focus-within {
        scroll-behavior: smooth;
      }

      /* Set core body defaults */
      body {
        min-height: 100vh;
        text-rendering: optimizeSpeed;
        line-height: 1.5;
      }

      /* A elements that don't have a class get default styles */
      a:not([class]) {
        text-decoration-skip-ink: auto;
      }

      /* Make images easier to work with */
      img,
      picture {
        max-width: 100%;
        display: block;
      }

      /* Inherit fonts for inputs and buttons */
      input,
      button,
      textarea,
      select {
        font: inherit;
      }

      /* Remove all animations, transitions and smooth scroll for people that prefer not to see them */
      @media (prefers-reduced-motion: reduce) {
        html:focus-within {
          scroll-behavior: auto;
        }

        *,
        *::before,
        *::after {
          animation-duration: 0.01ms !important;
          animation-iteration-count: 1 !important;
          transition-duration: 0.01ms !important;
          scroll-behavior: auto !important;
        }
      }

      /* ^^^ RESET */

      body {
        font-family: "Inter", sans-serif;
      }

      .gotobutton {
        text-align: center;
        display: block;
        text-decoration: none;
        background-color: white;
        color: #6b7280;
        padding: 0.5rem 1rem;
        border-radius: 4px;
      }
      .gotobutton:hover {
        background-color: #e5e7eb;
      }

      .gotobutton:active {
        background-color: #d1d5db;
      }

      .gotobutton:visited {
        background-color: #ccc;
      }

      .signature {
        text-align: right;
        font-size: 24px;
        font-family: "Caveat", cursive;
      }

      .spinner-2 {
        width: 75px;
        height: 75px;
        border-radius: 50%;
        background: radial-gradient(farthest-side, #3b82f6 94%, #0000) top/8px
            12px no-repeat,
          conic-gradient(#0000 30%, #3b82f6);
        -webkit-mask: radial-gradient(
          farthest-side,
          #0000 calc(100% - 12px),
          #000 0
        );
        animation: s3 1s infinite linear;
      }

      @keyframes s3 {
        100% {
          transform: rotate(1turn);
        }
      }
    </style>
  </head>
  <body>
    <div style="min-height: 100vh; padding: 2rem; display: flex">
      <div
        style="
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
        "
      >
        <div
          style="
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
            max-width: 32rem;
            border-radius: 8px;
            border-width: 1px;
            border-style: solid;
            border-color: #e5e7eb;
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 4rem;
            padding-right: 4rem;
          "
        >
          <div style="overflow: hidden; border-radius: 4px">
            <img
              style="
                height: 100%;
                display: block;
                object-fit: contain;
                width: 400px;
                padding-bottom: 2rem;
                border-bottom-width: 1px;
                border-bottom-style: solid;
                border-bottom-color: #e5e7eb;
              "
              src="https://www.wasatchbg.com/uploads/1/2/2/8/122827489/published/wasatch-benefits-group-logo.png?1577672207"
              alt=""
            />
          </div>

          <div>
            <p style="font-size: 1.5rem; text-align: center; padding-top: 2rem">
              Preparing your information now...
            </p>
            <div style="margin-top: 4rem">
              <div style="margin: auto" class="spinner-2"></div>
            </div>
          </div>

          <div
            style="
              margin-top: 8rem;
              border-top-width: 1px;
              border-top-style: solid;
              border-top-color: #e5e7eb;
            "
          >
            <div style="margin-top: 2rem">
              <a href="$REDIRECT_URL" class="gotobutton"
                >If you are not redirected shortly, click here
                <span>&#10230;</span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </body>
</html>


"""


SUPPORTED_STATUS_CODES = {
    "200": "OK",
    "301": "Moved Permanently",
    "302": "Found",
    "307": "Temporary Redirect",
}

# Check its not an api route
def check_is_apiroute(path):
    """Check its an api route or a redirectable slug"""
    LOGGER.info(f"Checking is api route: {path}")
    is_apiroute = False

    if path.startswith("docs"):
        is_apiroute = True
    if path.startswith("api/"):
        is_apiroute = True
    if path.startswith("openapi"):
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
def build_og_redirect(response, redirect_record):
    """Build the og redirect response"""

    og_settings = redirect_record.get("OgSettings", {})
    target_url = redirect_record.get("TargetUrl", {})

    # pull og values
    og_title = og_settings.get("OgTitle", "")
    og_description = og_settings.get("OgDescription", "")
    og_url = og_settings.get("OgUrl", "")
    og_image = og_settings.get("OgImage", "")
    og_image_alt = og_settings.get("OgImage_alt", "")

    html_page = (
        HTML_TEMPLATE.replace("$OG_TITLE", og_title)
        .replace("$OG_DESCRIPTION", og_description)
        .replace("$OG_URL", og_url)
        .replace("$OG_IMAGE", og_image)
        .replace("$OG_IMAGE_ALT", og_image_alt)
        .replace("$REDIRECT_URL", target_url)
    )

    response = {
        "status": "200",
        "statusDescription": "OK",
        "headers": {
            "cache-control": [{"key": "Cache-Control", "value": "max-age=100"}],
            "content-type": [{"key": "Content-Type", "value": "text/html"}],
        },
        "body": html_page,
    }

    return response


# Return redirect
def build_direct_redirect(response, redirect_record, status_code="301"):
    """Build the direct redirect response"""

    redirect_to_url = redirect_record.get("TargetUrl")
    LOGGER.info(f"Direct redirect to: {redirect_to_url}")

    response = {
        "status": status_code,
        "statusDescription": SUPPORTED_STATUS_CODES[status_code],
        "headers": {
            "cache-control": [{"key": "Cache-Control", "value": "max-age=100"}],
            "content-type": [{"key": "Content-Type", "value": "text/html"}],
            "location": [{"key": "Location", "value": redirect_to_url}],
        },
    }

    return response


def make_response(cloudfront_event):
    """Check the request and determine response"""

    request = cloudfront_event["request"]

    # request.uri is just the URL path without hostname or querystring
    requested_path = request["uri"]
    # Remove leading and ending slash
    requested_slug = requested_path.lstrip("/").rstrip("/")

    requested_method = request["method"]

    # Return original and let it continue
    if check_is_apiroute(requested_slug):
        LOGGER.info("Forward to API")
        return request

    # If its not a GET method, dont redirect
    if not check_is_getmethod(requested_method):
        LOGGER.info("Forward to API, not a GET")
        return request

    # Read slug from dynamodb to get redirect path
    redirect_record = get_redirect_record(requested_slug)

    if not redirect_record:
        LOGGER.info("Forward to API, no redirect recorded")
        redirect_record = {"TargetUrl": EXPIRED_REDIRECT}

    # Find target URL
    redirect_type = redirect_record.get("RedirectType")

    response = {
        "headers": request["headers"],
        "status": "200",
        "statusDescription": "OK",
    }

    # OG html type
    if redirect_type == "OG_HTML":
        response = build_og_redirect(response, redirect_record)

    # Direct type
    else:
        response = build_direct_redirect(response, redirect_record)

    return response


def handler(evt=None, ctx=None):
    """Handle viewer-request"""

    LOGGER.info(f"FULL EVENT: {evt}")

    try:
        #  Get the incoming request and the initial response from S3
        #  https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-event-structure.html
        cloudfront_event = evt["Records"][0]["cf"]

        res = make_response(cloudfront_event)

        return res

    except Exception as err:
        LOGGER.error("Failed with error: %s", err)
        raise err


# Different handler for each env to handle
# to set env variables, since cant pass in
# env variables to lambda @edge function


def handler_dev(evt=None, ctx=None):
    """dev env"""
    global KERTEYT_TABLE_NAME
    global EXPIRED_REDIRECT
    KERTEYT_TABLE_NAME = "cc-east-dev-db-kurteyt"
    EXPIRED_REDIRECT = "https://demo.currentclient.io/expired"
    return handler(evt, ctx)


def handler_prd(evt=None, ctx=None):
    """prd env"""
    global KERTEYT_TABLE_NAME
    global EXPIRED_REDIRECT
    KERTEYT_TABLE_NAME = "cc-east-prd-db-kurteyt"
    EXPIRED_REDIRECT = "https://app.currentclient.com/expired"
    return handler(evt, ctx)
