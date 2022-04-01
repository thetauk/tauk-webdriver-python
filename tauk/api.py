import logging
from datetime import datetime

import requests

from tauk.context.test_data import TestData
from tauk.exceptions import TaukException

logger = logging.getLogger('tauk')


class TaukApi:
    # _API_URL = 'http://localhost:5000/api/v1'
    _API_URL = 'https://requestinspector.com/inspect/01fzc1zd7xkp766hw753525sv1'
    run_id: str = None

    def __init__(self, api_token, project_id):
        self._api_token = api_token
        self._project_id = project_id

    def initialize_run_mock(self, test_data):
        self.run_id = 'runid-dfg'
        return self.run_id

    def initialize_run(self, test_data: TestData):
        url = f'{TaukApi._API_URL}/execution/{self._project_id}/initialize'
        body = {
            'language': test_data.language,
            'tauk_client_version': test_data.tauk_client_version,
            'start_timestamp': int(datetime.utcnow().timestamp() * 1000),
            'timezone': test_data.timezone,
            'dst': test_data.dst
        }

        headers = {
            'Authorization': f'Bearer {self._api_token}'
        }

        logger.debug(f'Initializing run with: url[{url}], headers[{headers}], body[{body}]')
        response = requests.post(url, json=body, headers=headers)
        if response.status_code != 200:
            logger.error(f'Failed to initialize Tauk execution. Response: {response.text}')
            raise TaukException('failed to initialize tauk execution')

        logger.debug(f'Response: {response.text}')
        self.run_id = response.json()['run_id']
        logger.info(f'Setting run ID for current execution as {self.run_id}')
        return self.run_id

    def test_start(self, test_name, file_name, start_time):
        url = f'{TaukApi._API_URL}/api/v1/execution/{self._project_id}/{self.run_id}/report/test/start'
        body = {
            'test_name': test_name,
            'file_name': file_name,
            'start_time': start_time,
        }

        headers = {
            'Authorization': f'Bearer {self._api_token}'
        }

        r = requests.post(url, body, headers)
        logger.info(f'Response: {r.json()}')
        # TODO: Validate response code
        return r.json()['test_id']

    def test_finish(self, test_name, file_name, start_time, end_time):
        url = f'{TaukApi._API_URL}/api/v1/execution/{self._project_id}/{self.run_id}/report/test/finish'
        body = {
            'test_name': test_name,
            'file_name': file_name,
            'start_time': start_time,
            'end_time': end_time,
        }

        headers = {
            'Authorization': f'Bearer {self._api_token}'
        }

        r = requests.post(url, body, headers)
        logger.info(f'Response: {r.json()}')
        # TODO: Validate response code
        return r.json()['test_id']

    def upload(self, test_data):
        url = f'{TaukApi._API_URL}/api/v1/execution/${self._project_id}/{self.run_id}/report/upload'
        body = test_data

        headers = {
            'Authorization': f'Bearer {self._api_token}'
        }

        logger.debug(f'Uploading test: url[{url}], headers[{headers}], body[{body}]')
        response = requests.post(url, body, headers)
        if response.status_code != 200:
            logger.error(f'Failed to upload test. Response: {response.text}')
            raise TaukException('failed to initialize tauk execution')

        logger.debug(f'Response: {response.text}')
