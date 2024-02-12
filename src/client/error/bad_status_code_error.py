__all__ = ["BadStatusCodeError"]


class BadStatusCodeError(RuntimeError):
    received_status_code: int
    expected_status_code: int

    def __init__(self, received_status_code: int, expected_status_code: int = 200):
        super().__init__(f"Server responded with status code other than {expected_status_code} ({received_status_code})")

        self.expected_status_code = expected_status_code
        self.received_status_code = received_status_code
