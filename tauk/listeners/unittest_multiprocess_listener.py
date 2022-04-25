import logging

from tauk.listeners.unittest_listener import TaukListener
from tauk.tauk_webdriver import Tauk

logger = logging.getLogger('tauk')


class TaukMultiprocessListener(TaukListener):

    def __init__(self, stream, descriptions, verbosity) -> None:
        logger.debug('Initializing Tauk Multiprocess listener')
        self.multiprocess_run = True
        self.cleanup_exec_context_on_exit = False
        Tauk(multi_process_run=self.multiprocess_run, cleanup_exec_context=self.cleanup_exec_context_on_exit)
        super().__init__(stream, descriptions, verbosity)
