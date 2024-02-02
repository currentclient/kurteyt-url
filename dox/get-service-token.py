"""get service auth token"""

import json

import boto3

# DEV
AWS_REGION = "us-west-2"
USERPOOL_ID = "us-west-2_prmFZ0Fif"
USERCLIENT_ID = "6dat4ip3ivr1b7sb4r5bcbqh09"
SECRET_NAME = "/cc/west/dev/user/users/service"

# PRD
# AWS_REGION = "us-west-2"
# USERPOOL_ID = "us-west-2_pDUWHeGaJ"
# USERCLIENT_ID = "3m83rvmir1a7qo8npivnci89a1"
# SECRET_NAME = "/cc/west/prd/user/users/service"

CLIENT_COGNITO = boto3.client("cognito-idp")
CLIENT_SSM = None
CACHED_PARAMS = {}


def get_param(param_name, is_decrypt=True):
    """Get param from ssm"""

    global CLIENT_SSM  # pylint: disable=global-statement

    if CLIENT_SSM is None:
        # Create a Secrets Manager client
        session = boto3.session.Session()
        CLIENT_SSM = session.client(service_name="ssm", region_name=AWS_REGION)

    # Check its in the runtime cache
    cached_secret = CACHED_PARAMS.get(param_name, False)

    if cached_secret:
        return cached_secret

    try:
        get_param_value_response = CLIENT_SSM.get_parameter(
            Name=param_name, WithDecryption=is_decrypt
        )
    except Exception as err:
        raise err

    else:
        secret = get_param_value_response.get("Parameter", {}).get("Value")

        # Put it in runtime cache
        CACHED_PARAMS.setdefault(param_name, secret)

    return secret


def authenticate(username, password):
    """Get jwt token from cognito for the user"""

    try:
        response = CLIENT_COGNITO.admin_initiate_auth(
            UserPoolId=USERPOOL_ID,
            ClientId=USERCLIENT_ID,
            AuthFlow="ADMIN_USER_PASSWORD_AUTH",
            AuthParameters={
                # "USERNAME": "username",
                # "PASSWORD": "password",
                "USERNAME": username,
                "PASSWORD": password,
            },
            # ClientMetadata={"string": "string"},
            # AnalyticsMetadata={"AnalyticsEndpointId": "string"},
            # ContextData={
            #     "IpAddress": "string",
            #     "ServerName": "string",
            #     "ServerPath": "string",
            #     "HttpHeaders": [
            #         {"headerName": "string", "headerValue": "string"},
            #     ],
            #     "EncodedData": "string",
            # },
        )

        # Get the jwt
        res_jwt = response.get("AuthenticationResult").get("AccessToken")

    except CLIENT_COGNITO.exceptions.UserNotFoundException as err:
        raise Exception("User not found")
    except CLIENT_COGNITO.exceptions.NotAuthorizedException as err:
        raise Exception("User credentials are not valid")
    except Exception as err:
        raise err

    return res_jwt


if __name__ == "__main__":
    raw_secrets = get_param(SECRET_NAME)

    service_account_creds = json.loads(raw_secrets)
    username = service_account_creds.get("username")
    password = service_account_creds.get("password")
    jwt = authenticate(username, password)
    print(jwt)
