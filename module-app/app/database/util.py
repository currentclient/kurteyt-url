"""
Util

Database utililty functions
"""


def get_dynamodb_update_syntax(update_fields):
    """Generate expression syntax for dyanamodb update_item"""
    # https://github.com/aws/aws-sdk-js/issues/1720#issuecomment-329800089

    # SET #State = :valState, #FirstName = :valFirstName
    expression_statement = "SET "

    expression_names = {}
    # {
    #   '#State': "State",
    #   '#FirstName': "FirstName"
    # }

    expression_attributes = {}
    # {
    #   ":valState": update_fields["State"],
    #   ":valFirstName": update_fields["FirstName"],
    # }

    for update_key, update_value in update_fields.items():
        # e.g. update_key = "Firstname"
        # e.g. update_value = "Franklin"

        # Add to expression statement
        expression_statement += f"#{update_key} = :val{update_key},"

        # Add to expression values
        expression_names.setdefault(f"#{update_key}", update_key)
        expression_attributes.setdefault(f":val{update_key}", update_value)

    # Strip off last comma at the end
    expression_statement = expression_statement[:-1]

    return expression_statement, expression_names, expression_attributes
