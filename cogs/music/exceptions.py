class MusicError(Exception):
    """
    Custom exception class for errors related to music operations.

    This exception is raised when there are issues with loading or playing songs in a music application.

    Attributes:
        message (str): A description of the error.
    """

    def __init__(self, message: str) -> None:
        self.message: str = message
        super().__init__(message)


class ResolveException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
