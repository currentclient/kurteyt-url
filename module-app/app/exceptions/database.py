"""
Database Exceptions

Exceptions to be used when connecting to database
"""


class DatabaseConnectionError(Exception):
    """Exception when connecting to database fails"""

    def __init__(self):
        super().__init__()
        self.message = "Failed to connect to database record"
        self.__cause__ = None
