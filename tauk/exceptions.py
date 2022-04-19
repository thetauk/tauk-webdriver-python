import logging

logger = logging.getLogger('tauk')


class TaukException(Exception):
    def __init__(self, msg='') -> None:
        logger.error(msg)
