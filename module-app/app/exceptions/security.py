"""
Security Exceptions

Exceptions to be used for security
"""


class NoCredentialsError(Exception):
    """Exception when credentials are not found"""

    def __init__(self):
        super().__init__()
        self.message = "Not authorized"
        self.__cause__ = None
