import gzip
import logging
import os
import platform
from datetime import datetime, timezone

import requests
from requests.adapters import HTTPAdapter

import tauk
from tauk.context.test_data import TestData
from tauk.enums import AttachmentTypes
from tauk.exceptions import TaukException
from tauk.utils import shortened_json

logger = logging.getLogger('tauk')

request_timeout = (3, 6)  # (Connection timeout, Receive data timeout)
POST = 'POST'
GET = 'GET'


class TaukApi:
    run_id: str = None

    def __init__(self, api_token, project_id, multi_process_run=False):
        self._TAUK_API_URL = 'https://www.tauk.com/api/v1'
        self._API_URL = os.environ.get('TAUK_API_URL', self._TAUK_API_URL)
        self._api_token = api_token
        self._project_id = project_id
        self._multi_process_run = multi_process_run

    def request(self, method, url, headers=None, data=None, timeout=request_timeout, **kwargs):
        tauk_adapter = HTTPAdapter(max_retries=3)
        if not headers:
            headers = {}
        headers.update({'Authorization': f'Bearer {self._api_token}'})
        with requests.Session() as session:
            session.mount(self._TAUK_API_URL, tauk_adapter)

            response = session.request(method, url, timeout=timeout, data=data, headers=headers, **kwargs)
            return response

    def set_token(self, api_token, project_id):
        self._api_token = api_token
        self._project_id = project_id

    def get_api_token(self):
        return self._api_token

    def get_project_id(self):
        return self._project_id

    def initialize_run(self, test_data: TestData, run_id: str = None):
        url = f'{self._API_URL}/execution/{self._project_id}/initialize'
        body = {
            'language': test_data.language,
            'tauk_client_version': test_data.tauk_client_version,
            'start_timestamp': int(datetime.now(tz=timezone.utc).timestamp() * 1000),
            'timezone': test_data.timezone,
            'dst': test_data.dst,
            'multi_process_run': self._multi_process_run,
            'host_os_name': platform.system(),
            'host_os_version': platform.platform(terse=True)
        }

        if run_id:
            body['run_id'] = run_id

        logger.debug(f'Initializing run with: url[{url}], body[{body}]')
        response = self.request(POST, url, json=body)
        if not response.ok:
            logger.error(f'Failed to initialize Tauk execution. Response[{response.status_code}]: {response.text}')
            raise TaukException('failed to initialize tauk execution')

        logger.debug(f'Response: {response.text}')
        self.run_id = response.json()['run_id']
        latest_client_versions = response.json().get('latest_tauk_client_version', tauk.__version__)
        if tauk.__version__ != 'develop' and latest_client_versions != tauk.__version__:
            logger.warning(f'You are currently using Tauk [{tauk.__version__}]. '
                           f'Consider updating to latest version [{latest_client_versions}] using '
                           f'"pip install -U tauk"')
        logger.info(f'Setting run ID for current execution as {self.run_id}')
        return self.run_id

    def test_start(self, test_name, file_name, start_time):
        url = f'{self._API_URL}/execution/{self._project_id}/{self.run_id}/report/test/start'
        body = {
            'test_name': test_name,
            'file_name': file_name,
            'start_time': start_time,
        }

        response = self.request(POST, url, json=body)
        logger.info(f'Response: {response.json()}')
        if not response.ok:
            logger.error(f'Failed to register test start. Response[{response.status_code}]: {response.text}')
            raise TaukException('failed to register test start')

        return response.json().get('external_test_id')

    def test_finish(self, test_name, file_name, start_time, end_time):
        url = f'{self._API_URL}/execution/{self._project_id}/{self.run_id}/report/test/finish'
        body = {
            'test_name': test_name,
            'file_name': file_name,
            'start_time': start_time,
            'end_time': end_time,
        }

        response = self.request(POST, url, json=body)
        logger.info(f'Response: {response.json()}')
        if not response.ok:
            logger.error(f'Failed to register test finish. Response[{response.status_code}]: {response.text}')
            raise TaukException('failed to register test finish')

        return response.json().get('external_test_id')

    def upload(self, test_data):
        url = f'{self._API_URL}/execution/{self._project_id}/{self.run_id}/report/upload'
        headers = {'Content-Type': 'application/json'}

        logger.debug(f'Uploading test: url[{url}], headers[{headers}], body[{shortened_json(test_data)}]')
        response = self.request(POST, url, data=test_data, headers=headers)
        if not response.ok:
            logger.error(f'Failed to upload test. Response[{response.status_code}]: {response.text}')
            raise TaukException('failed to upload test results')

        logger.debug(f'Response: {response.text}')
        return response.json().get('result')

    def upload_attachment(self, file_path, attachment_type: AttachmentTypes, test_id):
        if not test_id:
            raise TaukException(f'invalid test_id {test_id}')

        url = f'{self._API_URL}/execution/{self._project_id}/{self.run_id}/attachment/upload/{test_id}'

        headers = {'Tauk-Attachment-Type': f'{attachment_type.value}'}

        logger.debug(f'Uploading test attachment: url[{url}], headers[{headers}], file[{file_path}]')
        with open(file_path, 'rb') as file:
            response = self.request(POST, url, data=file, headers=headers)
            if not response.ok:
                logger.error(f'Failed to upload attachment. Response[{response.status_code}]: {response.text}')
                raise TaukException('failed to upload attachment')

            logger.debug(f'Response: {response.text}')

    def finish_execution(self, file_path=None):
        end_ts = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
        url = f'{self._API_URL}/execution/{self._project_id}/{self.run_id}/finish/{end_ts}'

        if not file_path:
            logger.debug(f'Sending execution finish: url[{url}]')
            response = self.request(POST, url)
            if not response.ok:
                logger.error(
                    f'Failed to upload execution error logs. Response[{response.status_code}]: {response.text}')
                raise TaukException('failed to upload execution error logs')
            return

        headers = {'Content-Encoding': 'gzip'}
        logger.debug(f'Sending execution finish: url[{url}], headers[{headers}], file[{file_path}]')
        with open(file_path, 'rb') as file:
            body = gzip.compress(file.read())
            response = self.request(POST, url, data=body, headers=headers)
            if not response.ok:
                logger.error(
                    f'Failed to upload execution error logs. Response[{response.status_code}]: {response.text}')
                raise TaukException('failed to upload execution error logs')

# TODO: Add API to remove browser
