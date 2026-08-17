class KnowledgeValidationError(ValueError):
    """
    Raised when persistent knowledge violates validation rules.
    """

    def __init__(
        self,
        code: str,
        message: str,
    ):
        self.code = code
        self.message = message

        super().__init__(
            f"{code}: {message}"
        )
