import logging

logger = logging.getLogger('tauk')


class TaukException(Exception):
    def __init__(self, msg='') -> None:
        pass
        # logger.error(msg)


class TaukTestMethodNotFound(TaukException):
    def __init__(self, msg='') -> None:
        super().__init__(msg)
