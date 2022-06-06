import logging
import os
import subprocess
import time
import requests

from tauk.assistant.config import AssistantConfig
from tauk.enums import AttachmentTypes
from tauk.exceptions import TaukException
from tauk.utils import get_open_port

logger = logging.getLogger('tauk')


class TaukAssistant:

    def __init__(self, api_token: str, execution_dir: str, config: AssistantConfig) -> None:
        self.config = config
        self._executable_path = os.getenv('TAUK_ASSISTANT_EXECUTABLE', 'tauk-assistant')
        self._api_token = api_token
        self._execution_dir = execution_dir
        self._process: subprocess.Popen | None = None
        self._assistant_port = 8285
        self._version = ''
        self._connections = {}

    def is_running(self) -> bool:
        return True if self._process and self._process.poll() is None else False

    def kill(self):
        self._process.kill()

    def launch(self):
        if self.is_running():
            raise TaukException(f'an instance of tauk assistant is already running at {self._assistant_port}')

        # TODO: Implement a more reliable way to lock the port since there could  be a race condition with multiple exec
        self._assistant_port = get_open_port(range(self._assistant_port, self._assistant_port + 10))
        if not self._assistant_port:
            raise TaukException('No free ports available in the range {range}')

        cmd = [self._executable_path,
               '-apiToken', self._api_token,
               '-executionDir', self._execution_dir,
               '-port', str(self._assistant_port)]
        logger.debug(f'[Assistant] Launching Tauk assistant app {" ".join(cmd)}')
        self._process = subprocess.Popen(' '.join(cmd), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait for assistant to launch
        t1 = time.time()
        while (time.time() - t1) < 6:  # Timeout after 6 seconds
            try:
                response = requests.get(f'http://localhost:{self._assistant_port}/version', timeout=3)
                if response.status_code == 200:
                    self._version = response.json()['version']
                    return
            except Exception:
                try:
                    out, err = self._process.communicate(timeout=1)
                    logger.error('[Assistant] STDOUT: %s', out)
                    logger.error('[Assistant] STDERR: %s', err)
                    raise TaukException(f'failed to launch tauk assistant')
                except subprocess.TimeoutExpired:
                    pass

        self.kill()
        raise TaukException('timed out trying to launch assistant app')

    def register_browser(self, debugger_address):
        logger.debug(f'[Assistant] Registering browser {debugger_address}')
        url = f'http://localhost:{self._assistant_port}/cdp/browser/new/{debugger_address}'
        response = requests.post(url)
        if response.status_code != 200:
            logger.error(f'[Assistant] Failed to register browser. Response: {response.text}')
            raise TaukException(f'failed to register browser {debugger_address}')
        self._connections[debugger_address] = None

    def unregister_browser(self, debugger_address):
        logger.debug(f'[Assistant] Unregistering browser {debugger_address}')
        url = f'http://localhost:{self._assistant_port}/cdp/browser/new/{debugger_address}'
        response = requests.delete(url)
        if response.status_code != 200:
            logger.error(f'[Assistant] Failed to unregister browser. Response: {response.text}')
            raise TaukException(f'failed to unregister browser {debugger_address}')

    def connect_page(self, debugger_address) -> str:
        logger.debug(f'[Assistant] Connecting to first page on {debugger_address}')
        url = f'http://localhost:{self._assistant_port}/cdp/browser/page/{debugger_address}/connect'

        response = requests.post(url, json=self.config.cdp_config)
        if response.status_code != 200:
            logger.error(
                f'[Assistant] Failed to connect to the page for {debugger_address}. Response: {response.text}')
            raise TaukException(f'failed to connect to browser page for {debugger_address}')

        page_id = response.json().get('desc').get('id')
        self._connections[debugger_address] = page_id
        return page_id

    def close_page(self, debugger_address):
        logger.debug(f'[Assistant] Closing page connection on {debugger_address}')
        # Set page to None because sometimes browser cane exit before calling close_page
        self._connections[debugger_address] = None
        url = f'http://localhost:{self._assistant_port}/cdp/browser/targets/{debugger_address}/close'
        response = requests.post(url)
        if response.status_code != 200:
            logger.error(
                f'[Assistant] Failed to close page connection for {debugger_address}. Response: {response.text}')
            raise TaukException(f'failed to close page connection for {debugger_address}')

        page_id = response.json().get('desc').get('id')  # TODO: Rename to "result" instead of "desc"
        return page_id

    def get_connected_page(self, debugger_address) -> str:
        return self._connections.get(debugger_address, None)

    def get_attachments(self, connected_page_id):
        attachment_path = os.path.join(self._execution_dir, 'assistant', connected_page_id)
        assistant_attachments = next(os.walk(attachment_path), (None, None, []))[2]  # only files
        attachments = []
        for attachment in assistant_attachments:
            attachments.append(
                (os.path.join(attachment_path, attachment), AttachmentTypes.resolve_assistant_log(attachment)))
        return attachments
