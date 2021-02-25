"""
Users Exceptions

Exceptions to be used for users things
"""


class GetProfileFailed(Exception):
    """Exception when get fails"""

    def __init__(self):
        super().__init__()
        self.message = "Failed to read users profile"
        self.__cause__ = None


class NoRegisteredUserNumber(Exception):
    """Exception when get fails"""

    def __init__(self):
        super().__init__()
        self.message = "User doesnt have a registered number"
        self.__cause__ = None
