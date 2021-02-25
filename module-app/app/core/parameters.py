"""
Parameters

Common parameters that can be used
"""

from fastapi import Query

param_limit = Query(
    100,
    title="Pagination Limit",
    description="Pagination page size",
    ge=10,
    le=100,
)


param_cursor = Query(
    None,
    title="Pagination Cursor",
    description="Pagination cursor provided by previous paginated response",
)
