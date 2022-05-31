import logging

logger = logging.getLogger('tauk')


class TaukException(Exception):
    def __init__(self, msg='') -> None:
        pass


class TaukTestMethodNotFoundException(TaukException):
    def __init__(self, msg='') -> None:
        super().__init__(msg)


class TaukInvalidTypeException(TaukException):
    def __init__(self, msg='') -> None:
        super().__init__(msg)
