#### ##########
# Error Codes #
###############

# 0: Internal Error
# 1: Missing code snippet from payload
# 2: Malformed payload field


class APIError(Exception):
    def __init__(self, message: str, error_code: int = 0):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
