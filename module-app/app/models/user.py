"""User Models"""

from typing import List, Optional, Union

from pydantic import BaseModel


class UserBase(BaseModel):
    """
    Base

    Used to provide fields and functions to more specific models
    Making everything optional, so that the update can inherit from base
    and not have to require anything
    """

    email: Optional[str] = None


class UserUpdate(UserBase):
    """
    Update

    Properties to receive on upload update
    """


class UserInDBBase(UserBase):
    """
    InDBBase

    Inherits from create, but on create Ids are added, dont include PK and Sk
    so that the Upload can be returned without them
    """

    user_id: str
    user_groups: Union[str, List[str]]
    is_admin: bool


class UserInDB(UserInDBBase):
    """
    InDB

    Properties properties stored in DB, this is full representation of
    record
    """


# Properties to return to client (wired in on endpoint as response_model)
class User(UserInDBBase):
    """
    Upload

    The model to be used for responses. Doesnt include internal PK and SK
    """
