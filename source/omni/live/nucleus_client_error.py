from fastapi import HTTPException

class NucleusClientError(HTTPException):
    def __init__(self, message, original_exception=None):
        self.message = f"Error connecting to Nucleus - {message}"
        if original_exception:
            self.message = f"{self.message}: {original_exception}"

        super().__init__(detail=self.message, status_code=502)
