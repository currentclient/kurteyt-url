"""Trunacate"""

import boto3

dynamo = boto3.resource("dynamodb")


def truncate_table(table_name):
    """nuclear option"""
    table = dynamo.Table(table_name)

    # get the table keys
    table_key_names = [key.get("AttributeName") for key in table.key_schema]

    # Only retrieve the keys for each item in the table (minimize data transfer)
    projection_expression = ", ".join(table_key_names)

    response = table.scan(projection_expression)
    data = response.get("Items")

    while "LastEvaluatedKey" in response:
        response = table.scan(
            projection_expression, ExclusiveStartKey=response["LastEvaluatedKey"]
        )
        data.extend(response["Items"])

    with table.batch_writer() as batch:
        for each in data:
            print(each)
            batch.delete_item(Key={key: each[key] for key in table_key_names})


# Add Table name
truncate_table("TABLE_NAME")
