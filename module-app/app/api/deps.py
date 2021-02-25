"""
Deps

Provides functions to be used as dependencies in routes. These functions will
raise HTTPExceptions
"""

from typing import List, Union

from fastapi import Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from app import models
from app.core.logger import get_logger
from app.core.security import JWTAuthorizationCredentials, JWTBearer

LOGGER = get_logger(__name__)


def get_current_jwt_user(
    credentials: JWTAuthorizationCredentials = Depends(JWTBearer()),
) -> models.User:
    """
    Get current user from jwt credentials

    Args:
        credentials: JWT Credentials

    Raises:
        HTTPException

    """
    LOGGER.debug("Function: get_current_jwt_user")
    # LOGGER.debug(f"Function: get_current_jwt_user | credentials: {credentials}")

    user_id: str

    try:

        user_id = str(credentials.claims.get("username"))

        user_groups: Union[str, List[str]] = credentials.claims.get(
            "cognito:groups", []
        )

        is_admin_group = bool("admins" in user_groups)
        is_services_group = bool("services" in user_groups)

        is_admin = is_services_group or is_admin_group

    except KeyError as err:
        LOGGER.exception(err)
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Username missing")

    user = models.User(user_id=user_id, user_groups=user_groups, is_admin=is_admin)

    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_jwt_user),
) -> models.User:
    """
    Get current user from jwt credentials checking if they are active

    Args:
        current_user: A User model

    Raises:
        HTTPException

    """
    LOGGER.debug("Function: get_current_active_user")
    # if not crud.user.is_active(current_user):
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
