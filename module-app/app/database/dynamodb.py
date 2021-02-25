"""
DynamoDB

All interactions with dynamodb, this handles all interactions with database

"""

from enum import Enum
from os import environ
from typing import Any, Dict

import boto3
from pydantic.main import BaseModel

from app import exceptions
from app.core.logger import get_logger
from app.database import util

# Setup boto3
AWS_REGION = environ.get("AWS_REGION")


# from boto3.dynamodb.conditions import Attr, Key


class UpdateReturnValues(str, Enum):
    """Update return options"""

    all_new = "ALL_NEW"
    updated_new = "UPDATED_NEW"


class BatchWriteOperations(str, Enum):
    """Batch write options"""

    put = "PUT"
    delete = "DELETE"


class ConditionExpressionOperator(str, Enum):
    """Condition expression operators"""

    NOT_EXISTS = "NOT_EXISTS"


class ConditionExpression(BaseModel):
    """
    ConditionExpression

    A condition expression, to be translated to dynamodb condition expression
    """

    Attribute: str
    Operator: ConditionExpressionOperator


LOGGER = get_logger(__name__)


# Lazy initialize boto3 resources
RES_DYNAMODB = None


def _get_table(table: str) -> "boto3.resources.factory.dynamodb.Table":
    """
    Get dynamodb kurteyt table resource handle

    Raises:
        DatabaseConnectionError

    """

    global RES_DYNAMODB  # pylint: disable=global-statement

    if RES_DYNAMODB is None:
        RES_DYNAMODB = (  # pylint: disable=redefined-outer-name,invalid-name
            boto3.resource("dynamodb", region_name=AWS_REGION)
        )

    try:
        res_table: "boto3.resources.factory.dynamodb.Table" = RES_DYNAMODB.Table(table)

        return res_table
    except (
        RES_DYNAMODB.meta.client.exceptions.ResourceNotFoundException,
        Exception,
    ) as err:
        LOGGER.exception(err)
        raise exceptions.DatabaseConnectionError()


class DynamoDB:
    """
    DynamoDB API Interactions

    Methods to handle all interation with database. Resuable and composable. This is
    the only class in application that interacts with the database.

    """

    def __init__(
        self,
        table: str,
    ):
        """
        Interactions with

        Args:
            table: A Dynamodb Table Name

        """
        self.table_name = table
        # Dynamodb Boto3 Table Resource
        self.Table = _get_table(self.table_name)

    def put_item(
        self, *, record: Dict, condition_expression: ConditionExpression = None
    ) -> Dict:
        """
        Dynamodb Table put_item

        Args:
            record: A json dictionary
            condition_expression: conditional expression to include

        Raises:
            CreateRecordFailed

        """
        LOGGER.debug(
            f"Function: put_item | Table: {self.table_name} | record: {record}"
        )

        dynamodb_condition_expression = None

        put_request = {"Item": record}

        if condition_expression:
            # Convert to dynamodb syntax
            dynamodb_condition_expression = self._convert_condition_expression(
                condition_expression
            )

            put_request["ConditionExpression"] = dynamodb_condition_expression

        try:
            # Run db action
            self.Table.put_item(**put_request)
        except self.Table.meta.client.exceptions.ConditionalCheckFailedException as err:
            LOGGER.info("Write with conditional failed condition")
            raise exceptions.CreateRecordConditionFailed()
        except Exception as err:
            LOGGER.exception(err)
            raise exceptions.CreateRecordFailed()

        return record

    def get_item_by_pk(self, pk: str) -> Dict[Any, Any]:
        """
        Dynamodb Table get_item

        Args:
            pk: PK for the record

        Raises:
            GetRecordFailed

        """
        LOGGER.debug(
            (
                f"Function: get_item_by_pk | Table: {self.table_name} |",
                f"PK: {pk}",
            )
        )

        try:

            # Get Item
            response = self.Table.get_item(
                Key={"PK": pk}
                # AttributesToGet=[
                #     'string',
                # ],
                # ConsistentRead=True | False,
                # ReturnConsumedCapacity='INDEXES' | 'TOTAL' | 'NONE',
                # ProjectionExpression='string',
                # ExpressionAttributeNames={
                #     'string': 'string'
                # }
            )

            record = response.get("Item", False)

            return record

        except Exception as err:
            LOGGER.exception(err)
            raise exceptions.GetRecordFailed()

    def update_item(
        self,
        *,
        pk: str,
        update_data: Dict,
        return_values: UpdateReturnValues = UpdateReturnValues.updated_new,
    ) -> Dict:
        """
        Dynamodb Table update_item

        Args:
            pk: Partition key
            sk: Sort key
            update_data: Data to be update

        Raises:
            UpdateRecordFailed

        """

        LOGGER.debug(
            (
                f"Function: update_item | Table: {self.table_name} |",
                f"pk: {pk}",
            )
        )
        LOGGER.log_json(update_data)

        try:
            # Generate dynamodb update syntax from input fields
            (
                expression_statement,
                expression_names,
                expression_values,
            ) = util.get_dynamodb_update_syntax(update_data)

            # Run db action
            response = self.Table.update_item(
                Key={
                    # PK is on the record being passed in for updates
                    "PK": pk
                },
                UpdateExpression=expression_statement,
                ExpressionAttributeNames=expression_names,
                ExpressionAttributeValues=expression_values,
                ReturnValues=return_values,
            )
        except Exception as err:
            LOGGER.exception(err)
            raise exceptions.UpdateRecordFailed()

        return response.get("Attributes")

    def delete_item(self, *, pk: str) -> Any:
        """
        Dynamodb Table delete_item

        Args:
            pk: Partition key
            sk: Sort key

        Raises:
            DeleteRecordFailed

        """
        LOGGER.debug(
            f"Function: delete_item | Table: {self.table_name} |",
            f"pk: {pk}",
        )

        try:
            # Run db action
            self.Table.delete_item(
                Key={
                    # PK and SK are on the record being passed in
                    "PK": pk,
                }
            )
        except Exception as err:
            LOGGER.exception(err)
            raise exceptions.DeleteRecordFailed()

        return pk

    def _query(
        self,
        req_query: Dict,
        limit: str = None,
        start_key: Dict = None,
    ) -> Any:
        """
        Run query

        Args:
            res_query: Request query object
            limit: Override limit in req_query
            start_key: Override exclusive start key

        Raises:
            QueryFailed

        """
        try:
            use_req_query = req_query

            # Override limit if its provided
            use_limit = limit or req_query.get("Limit", False)

            # Use the supplied query
            if use_limit:
                use_req_query = {**use_req_query, "Limit": use_limit}

            # Add start key
            if start_key:
                use_req_query = {
                    **use_req_query,
                    "ExclusiveStartKey": start_key,
                }

            # Query table
            res_query = self.Table.query(**use_req_query)

        except Exception as err:
            LOGGER.exception(err)
            raise exceptions.QueryFailed()

        return res_query

    @staticmethod
    def _convert_condition_expression(condition_expression: ConditionExpression) -> str:
        """Convert condition expression objects to string for dynamo"""

        dynamodb_expression = None

        try:

            if (
                ConditionExpressionOperator(condition_expression.Operator)
                is ConditionExpressionOperator.NOT_EXISTS
            ):
                dynamodb_expression = (
                    f"attribute_not_exists({condition_expression.Attribute})"
                )

        except Exception as err:
            LOGGER.info(f"Condition expression is invalid with error {err}")

        return dynamodb_expression
