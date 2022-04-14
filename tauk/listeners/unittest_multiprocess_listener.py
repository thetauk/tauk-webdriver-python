import logging

from tauk.listeners.unittest_listener import TaukListener
from tauk.tauk_webdriver import Tauk

logger = logging.getLogger('tauk')


class TaukMultiprocessListener(TaukListener):

    def __init__(self, stream, descriptions, verbosity) -> None:
        self.multiprocess_run = True
        Tauk(multi_process_run=True)
        super().__init__(stream, descriptions, verbosity)
