"""
Responses

Common responses that can be used
"""

from fastapi import status

common_400_and_500 = {
    status.HTTP_400_BAD_REQUEST: {
        "description": "Invalid user request",
        "content": {
            "application/json": {
                "example": {"detail": "A message for why the request is invalid"}
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Server error",
        "content": {
            "application/json": {
                "example": {"detail": "A message for why the server failed"}
            }
        },
    },
}
