"""
CRUD ShortUrls

Provides shorturls crud operations.
"""

from os import environ

from app import exceptions, models
from app.core.logger import get_logger
from app.crud.base import CRUDBase

LOGGER = get_logger(__name__)

KURTEYT_TABLE: str = environ.get("KURTEYT_TABLE", "")


class CRUDShortUrl(
    CRUDBase[
        models.ShortUrl,
        models.ShortUrlInDB,
        models.ShortUrlCreate,
        models.ShortUrlUpdate,
    ]
):
    """
    CRUD shorturls

    Methods to manage shorturls. Inherits from base crud to reuse common patterns.
    """

    def get_shorturl(self, shorturl_in: str) -> models.ShortUrlInDB:
        """
        Get shorturl

        Raises:
            RecordNotFound
            GetRecordFailed

        """

        shorturl_in_db = self.read_item_by_pk(partition=shorturl_in)

        return shorturl_in_db

    def create_shorturl(
        self, *, obj_in_create: models.ShortUrlCreate
    ) -> models.ShortUrl:
        """
        Create shorturl record

        Args:
            obj_in_create: A ShortUrl Create model

        Raises:
            ConvertToJsonFailed
            CreateRecordFailed

        """
        LOGGER.debug(f"Function: create_shorturl | obj_in_create: {obj_in_create}")

        try:

            # Prepare the shorturl create object by adding ids and keys
            obj_in_db = models.convert_shorturlcreate_to_shorturlindb(
                create_model=obj_in_create
            )

            obj_in_db_res = self.create(obj_in_db=obj_in_db)

            # Return object
            return obj_in_db_res

        except (
            exceptions.ConvertToJsonFailed,
            exceptions.CreateRecordFailed,
            Exception,
        ) as err:
            LOGGER.exception(err)
            raise err


shorturl = CRUDShortUrl(models.ShortUrl, models.ShortUrlInDB, KURTEYT_TABLE)
