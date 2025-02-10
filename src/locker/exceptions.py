class LockerException(Exception):
    """
    사물함 제어 관련 예외
    Exception for locker control
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)