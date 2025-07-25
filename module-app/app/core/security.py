"""Security"""

from typing import Dict, List, Optional, Union

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN

from app import exceptions
from app.core.logger import get_logger

LOGGER = get_logger(__name__)


class JWTAuthorizationCredentials(HTTPAuthorizationCredentials):
    """JWT credentials"""

    header: Dict[str, str]
    claims: Dict[str, Union[str, List[str], int]]
    signature: Optional[str] = None
    message: Optional[str] = None


class JWTBearer(HTTPBearer):
    """
    JWTBearer

    Checks Bearer token has been sent in request. HTTPBearer is doing that work.
    Parses token and returns body of token for downstream
    """

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    # When JWTBearer is called, receive the request
    async def __call__(self, request: Request) -> Optional[JWTAuthorizationCredentials]:
        """Get credential information when called"""

        # Grab creds from the request, using the HTTPBearer methods, which
        # will return auth creds
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(
            request
        )

        jwt_credentials = None

        try:
            try:

                jwt_token = credentials.credentials

                # message, signature = jwt_token.rsplit(".", 1)

                jwt_credentials = JWTAuthorizationCredentials(
                    scheme=credentials.scheme,
                    credentials=credentials.credentials,
                    header=jwt.get_unverified_header(jwt_token),
                    claims=jwt.get_unverified_claims(jwt_token),
                    # signature=signature,
                    # message=message,
                )
            except Exception as err:
                # Raise error since credentials didnt come through
                LOGGER.exception(err)
                raise exceptions.NoCredentialsError()

        except JWTError as err:
            LOGGER.exception(err)
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Invalid credentials"
            )
        except Exception as err:
            LOGGER.exception(err)
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not Authorized")

        return jwt_credentials
