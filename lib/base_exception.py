class PrestoBaseException(Exception):
    def __init__(self, message: str, error_code: int = 500):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

    def __str__(self):
        return f"{self.error_code}: {self.message}"