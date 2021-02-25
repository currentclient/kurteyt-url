"""
CRUD Base

Provides common crud operations.
"""

from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from app import database, exceptions
from app.core import logger, util

LOGGER = logger.get_logger(__name__)

ModelType = TypeVar("ModelType", bound=BaseModel)
ModelInDBType = TypeVar("ModelInDBType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, ModelInDBType, CreateSchemaType, UpdateSchemaType]):
    """
    CRUD base

    Methods to crud on database. Intended to be designed for reuse.

    Usage:
        CRUDBase[
            models.Kurteyt,
            models.KurteytInDB,
            models.KurteytCreate,
            models.KurteytUpdate,
            models.KurteytsPaginated,
        ]
    """

    def __init__(
        self,
        model: Type[ModelType],
        model_in_db: Type[ModelInDBType],
        table: str,
    ):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        Args:
            model: A model class
            model_in_db: A model class
            table: A Dynamodb Table Name

        """
        self.model = model
        self.model_in_db = model_in_db
        self.table_name = table
        self.db = database.DynamoDB(table=table)

    def create(
        self,
        *,
        obj_in_db: ModelInDBType,
        condition_expression: database.ConditionExpression = None,
    ) -> ModelInDBType:
        """
        Create record for the supplied object

        Args:
            obj_in_db: A model type
            condition_expression: Conditional expression on the write

        Raises:
            ConvertToJsonFailed
            CreateRecordFailed

        """
        LOGGER.debug(
            f"Function: create | Table: {self.table_name} | obj_in_db: {obj_in_db}"
        )

        try:
            # Get to json dict to be used by dynamodb client
            obj_in_db_json = jsonable_encoder(obj_in_db)
        except Exception as err:
            LOGGER.exception(err)
            raise exceptions.ConvertToJsonFailed()

        self.db.put_item(
            record=obj_in_db_json, condition_expression=condition_expression
        )

        return obj_in_db

    def read_item_by_pk(
        self, *, partition: str, is_full_key: bool = False
    ) -> ModelInDBType:
        """
        Get record for user id

        Args:
            partition: Id to be used by model.make_pk
            is_full_key: Flag to idenity the provided keys as complete or fallback to
                making keys with model.make_pk and model.sk

        Raises:
            GetRecordFailed
            RecordNotFound

        """
        LOGGER.debug(f"Function: read_item_by_pk_and_sk | partition: {partition}")

        try:

            pk_full = partition

            if not is_full_key:
                pk_full = self.model.make_pk(partition)

            # Get record
            record = self.db.get_item_by_pk(pk=pk_full)

            if not record:
                raise exceptions.RecordNotFound()

            # Convert record to model
            model_in_db_obj = self.model_in_db(**record)

            # Return new object
            return model_in_db_obj

        except (
            exceptions.GetRecordFailed,
            exceptions.RecordNotFound,
            Exception,
        ) as err:
            LOGGER.exception(err)
            raise err

    def update(
        self,
        *,
        db_obj: ModelInDBType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        return_values: Optional[
            database.UpdateReturnValues
        ] = database.UpdateReturnValues.updated_new,
    ) -> UpdateSchemaType:
        """
        Update record

        Prepare dynamodb syntax for updating an item and execute update on table

        Args:
            db_obj: A model type
            obj_in: A model type or a dictionary

        Raises:
            ConvertToJsonFailed
            UpdateRecordFailed

        """
        LOGGER.debug(f"Function: update | Table: {self.table_name}")

        # Get update object in right format
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        # Update the original model with the new data
        # for field in obj_data:
        #     if field in update_data:
        #         setattr(db_obj, field, update_data[field])

        # Convert to json
        try:
            db_obj_data = jsonable_encoder(db_obj)
        except Exception as err:
            LOGGER.exception(err)
            raise exceptions.ConvertToJsonFailed()

        try:
            current_timestamp = util.get_current_datetime()
            update_data["UpdatedAt"] = current_timestamp
        except Exception as err:
            LOGGER.exception("Failed to get update at time on record")

        response = self.db.update_item(
            pk=db_obj_data["PK"],
            sk=db_obj_data["SK"],
            update_data=update_data,
            return_values=return_values,
        )

        return response

    def delete(
        self,
        *,
        db_obj: ModelInDBType,
    ) -> Any:
        """
        Delete record

        Args:
            db_obj: A model type

        Raises:
            ConvertToJsonFailed
            DeleteRecordFailed

        """
        LOGGER.debug(
            f"Function: delete | Table: {self.table_name}",
        )

        try:
            db_obj_data = jsonable_encoder(db_obj)
        except Exception as err:
            LOGGER.exception(err)
            raise exceptions.ConvertToJsonFailed()

        self.db.delete_item(pk=db_obj_data["PK"])

        return db_obj
