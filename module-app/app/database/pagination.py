"""
Dynamodb Pagination

Provides class to handle pagination interactions.
"""

import base64
import json
from typing import Dict, Optional, Tuple

from pydantic import BaseModel

from app.core.logger import get_logger

LOGGER = get_logger(__name__)

# Pagination cursor class
class PaginationCursor(BaseModel):
    """
    PaginationCursor

    Methods to help encode and decode a pagination cursor.

    Usage:
        last_evaluated_key, limit = database.pagination.PaginationCursor.decode(
            cursor=cursor
        )
    """

    last_evaluated_key: Dict[str, str]
    limit: int
    projection_expression: Optional[str] = None

    def encode(self):
        """Create pagination cursor for dyanamodb"""
        # https://hackernoon.com/guys-were-doing-pagination-wrong-f6c18a91b232

        # TODO: handle filters as well - maybe for clientforms (databasefilter, contacts called them segmentfilters)

        # 1) Create a JSON object to capture the data needed to fetch next page
        cursor_json = {
            "lastEvaluatedKey": self.last_evaluated_key,
            "limit": self.limit,
            "projectionExpression": self.projection_expression,
        }

        # 2) base64 encode the JSON string
        cursor_encoded = json.dumps(cursor_json).encode()
        cursor_base64 = base64.urlsafe_b64encode(cursor_encoded).decode()

        # 3) return the base64 blob as cursor
        return cursor_base64

    @staticmethod
    def decode(cursor: str) -> Tuple[str, int, str]:
        """Parse pagination cursor for dyanamodb"""

        cursor_json = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())

        last_evaluated_key = cursor_json["lastEvaluatedKey"]
        limit = cursor_json["limit"]
        projection_expression = cursor_json["projectionExpression"]

        LOGGER.debug(cursor_json)

        return last_evaluated_key, limit, projection_expression
