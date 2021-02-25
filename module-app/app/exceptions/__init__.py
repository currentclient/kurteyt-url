"""Exceptions"""

from app.exceptions.base import (
    BatchWriteRecordsFailed,
    ConvertToJsonFailed,
    CreateRecordConditionFailed,
    CreateRecordFailed,
    DeleteRecordFailed,
    DeleteRecordVersionsFailed,
    GetRecordFailed,
    PaginationCursorInvalid,
    ParseResponseFailed,
    QueryFailed,
    ReadRecordFailed,
    RecordNotFound,
    ScanFailed,
    UnauthorizedRequest,
    UpdateRecordFailed,
)
from app.exceptions.database import DatabaseConnectionError
from app.exceptions.security import NoCredentialsError
from app.exceptions.users import GetProfileFailed, NoRegisteredUserNumber
