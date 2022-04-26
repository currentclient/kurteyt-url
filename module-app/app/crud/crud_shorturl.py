"""
CRUD ShortUrls

Provides shorturls crud operations.
"""

from os import environ

from app import database, exceptions, models
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

    def get_shorturl(self, short_id: str) -> models.ShortUrlInDB:
        """
        Get shorturl

        Raises:
            RecordNotFound
            GetRecordFailed

        """

        shorturl_in_db = self.read_item_by_pk(partition=short_id)

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

            # Add conditional, as to not overwrite this broadcast if already existing
            condition_expression = database.ConditionExpression(
                Attribute="PK",
                Operator=database.ConditionExpressionOperator.NOT_EXISTS,
            )

            obj_in_db_res = self.create(
                obj_in_db=obj_in_db, condition_expression=condition_expression
            )

            # Return object
            return obj_in_db_res

        except (exceptions.CreateRecordConditionFailed,) as err:
            LOGGER.exception(err)
            raise err
        except (
            exceptions.ConvertToJsonFailed,
            exceptions.CreateRecordFailed,
            Exception,
        ) as err:
            LOGGER.exception(err)
            raise err


shorturl = CRUDShortUrl(models.ShortUrl, models.ShortUrlInDB, KURTEYT_TABLE)
