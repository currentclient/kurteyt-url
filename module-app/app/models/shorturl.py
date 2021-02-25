"""ShortUrl Models"""

import datetime
import random
import string
from typing import Optional

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from app.core import util
from app.core.logger import get_logger

LOGGER = get_logger(__name__)


class ShortUrlBase(BaseModel):
    """
    ShortUrlBase

    Base shorturl contains the target url and the short url that will
    redirect to it.
    """

    TargetUrl: Optional[str] = None
    ShortUrl: Optional[str] = None
    NumDaysUntilExpire: Optional[int] = None
    TTL: Optional[int] = None

    @classmethod
    def make_pk(cls, shorturl: str):
        """Make PK"""
        return f"{cls.get_pk_hash()}{shorturl}"

    @staticmethod
    def get_pk_hash():
        """Get PK prefix hash"""
        return "SHORTURL#"


class ShortUrlCreate(BaseModel):
    """
    Create

    Properties to receive on shorturl creation
    """

    TargetUrl: str
    NumDaysUntilExpire: int = 90


class ShortUrlUpdate(ShortUrlCreate):
    """
    Update

    Properties to receive on shorturl update
    """


class ShortUrlInDBBase(ShortUrlBase):
    """
    InDBBase

    Inherits from create, but on create Ids are added, dont include PK and Sk
    so that the ShortUrl can be returned without them
    """

    CreatedAt: str


class ShortUrlInDB(ShortUrlInDBBase):
    """
    InDB

    Properties properties stored in DB, this is full representation of
    record
    """

    TargetUrl: str
    ShortUrl: str
    # Duplicating ids but adding dynamodb hash for access pattern readability
    PK: str  # SHORTURL#ShortUrl


# Properties to return to client (wired in on endpoint as response_model)
class ShortUrl(ShortUrlInDBBase):
    """
    ShortUrl

    The model to be used for responses. Doesnt include internal PK and SK
    """


# Model converters


def random_alnum(size=6):
    """Generate random 6 character alphanumeric string"""
    # List of characters [a-zA-Z0-9]
    chars = string.ascii_letters + string.digits
    code = "".join(random.choice(chars) for _ in range(size))
    return code


def convert_shorturlcreate_to_shorturlindb(
    create_model: ShortUrlCreate,
) -> ShortUrlInDB:
    """Convert ShortUrlCreate => ShortUrlInDB model"""

    # Generate unique url slug
    short_url = random_alnum(size=8)

    expire_datetime = datetime.datetime.today() + datetime.timedelta(
        days=create_model.NumDaysUntilExpire
    )
    expire_ttl = expire_datetime.timestamp()

    # Get timestamp
    current_timestamp = util.get_current_datetime()

    indb_model = ShortUrlInDB(
        # Add shorturl create values
        **jsonable_encoder(create_model),
        # Add Ids
        ShortUrl=short_url,
        TTL=expire_ttl,
        CreatedAt=current_timestamp,
        # Add pk and sk for dynamodb access patterns
        PK=ShortUrlBase.make_pk(shorturl=short_url),
    )

    return indb_model
