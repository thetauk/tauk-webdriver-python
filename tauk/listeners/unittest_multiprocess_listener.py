import logging

from tauk.config import TaukConfig
from tauk.listeners.unittest_listener import TaukListener
from tauk.tauk_webdriver import Tauk

logger = logging.getLogger('tauk')


class TaukMultiprocessListener(TaukListener):

    def __init__(self, stream, descriptions, verbosity) -> None:
        logger.debug('Initializing Tauk Multiprocess listener')

        tauk_config = TaukConfig(multiprocess_run=True)
        tauk_config.cleanup_exec_context = False
        Tauk(tauk_config)

        super().__init__(stream, descriptions, verbosity)
