"""
Base Exceptions

Exceptions to be used in the base crud operations.
"""


class UnauthorizedRequest(Exception):
    """Exception when unauthorized"""

    def __init__(self):
        super().__init__()
        self.message = "Unathorized"
        self.__cause__ = None


class CreateRecordFailed(Exception):
    """Exception when creating record fails"""

    def __init__(self):
        super().__init__()
        self.message = "Failed to create record"
        self.__cause__ = None


class CreateRecordConditionFailed(Exception):
    """Exception when creating record conditional fails"""

    def __init__(self):
        super().__init__()
        self.message = "Failed to create record with condition"
        self.__cause__ = None


class ReadRecordFailed(Exception):
    """Exception when reading a record fails"""

    def __init__(self):
        super().__init__()
        self.message = "Failed to read record"
        self.__cause__ = None


class UpdateRecordFailed(Exception):
    """Exception when updating a record fails"""

    def __init__(self):
        super().__init__()
        self.message = "Failed to update record"
        self.__cause__ = None


class DeleteRecordFailed(Exception):
    """Exception when deleting a record fails"""

    def __init__(self):
        super().__init__()
        self.message = "Failed to delete record"
        self.__cause__ = None


class DeleteRecordVersionsFailed(Exception):
    """Exception when deleting a records version fails"""

    def __init__(self):
        super().__init__()
        self.message = "Failed to delete record and its version"
        self.__cause__ = None


class BatchWriteRecordsFailed(Exception):
    """Exception when batch creating record fails"""

    def __init__(self):
        super().__init__()
        self.message = "Failed to batch record"
        self.__cause__ = None


class GetRecordFailed(Exception):
    """Exception when creating record fails"""

    def __init__(self):
        super().__init__()
        self.message = "Failed to get record"
        self.__cause__ = None


class RecordNotFound(Exception):
    """Exception when no record found"""

    def __init__(self):
        super().__init__()
        self.message = "Record not found"
        self.__cause__ = None


class PaginationCursorInvalid(Exception):
    """Exception when pagination cursor is invalid"""

    def __init__(self):
        super().__init__()
        self.message = "Pagination cursor is invalid"
        self.__cause__ = None


class QueryFailed(Exception):
    """Exception when query operation failes"""

    def __init__(self):
        super().__init__()
        self.message = "Query failed"
        self.__cause__ = None


class ScanFailed(Exception):
    """Exception when scan operation failed"""

    def __init__(self):
        super().__init__()
        self.message = "Scan failed"
        self.__cause__ = None


class ParseResponseFailed(Exception):
    """Exception when parsing the response failed"""

    def __init__(self):
        super().__init__()
        self.message = "Response couldnt be read"
        self.__cause__ = None


class ConvertToJsonFailed(Exception):
    """Exception when converting the input to json failed"""

    def __init__(self):
        super().__init__()
        self.message = "Couldnt be converted to json"
        self.__cause__ = None
