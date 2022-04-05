import logging
import os
from datetime import datetime

import requests

from tauk.context.test_data import TestData
from tauk.exceptions import TaukException
from tauk.utils import shortened_json

logger = logging.getLogger('tauk')


class TaukApi:
    _API_URL = 'https://www.tauk.com/api/v1'
    run_id: str = None

    def __init__(self, api_token, project_id):
        self._API_URL = os.environ.get('TAUK_API_URL', self._API_URL)
        self._api_token = api_token
        self._project_id = project_id

    def initialize_run_mock(self, test_data, run_id=None):
        self.run_id = '5d917db6-cf5d-4f30-8303-6eefc35e7558'
        return self.run_id

    def initialize_run(self, test_data: TestData, run_id: str = None):
        url = f'{TaukApi._API_URL}/execution/{self._project_id}/initialize'
        body = {
            'language': test_data.language,
            'tauk_client_version': test_data.tauk_client_version,
            'start_timestamp': int(datetime.utcnow().timestamp() * 1000),
            'timezone': test_data.timezone,
            'dst': test_data.dst
        }

        if run_id:
            body['run_id'] = run_id

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
        url = f'{TaukApi._API_URL}/execution/{self._project_id}/{self.run_id}/report/test/start'
        body = {
            'test_name': test_name,
            'file_name': file_name,
            'start_time': start_time,
        }

        headers = {
            'Authorization': f'Bearer {self._api_token}'
        }

        response = requests.post(url, json=body, headers=headers)
        logger.info(f'Response: {response.json()}')
        # TODO: Validate response code
        return response.json()['test_id']

    def test_finish(self, test_name, file_name, start_time, end_time):
        url = f'{TaukApi._API_URL}/execution/{self._project_id}/{self.run_id}/report/test/finish'
        body = {
            'test_name': test_name,
            'file_name': file_name,
            'start_time': start_time,
            'end_time': end_time,
        }

        headers = {
            'Authorization': f'Bearer {self._api_token}'
        }

        response = requests.post(url, json=body, headers=headers)
        logger.info(f'Response: {response.json()}')
        # TODO: Validate response code
        return r.json()['test_id']

    def upload(self, test_data):
        url = f'{TaukApi._API_URL}/execution/{self._project_id}/{self.run_id}/report/upload'
        body = test_data

        headers = {
            'Authorization': f'Bearer {self._api_token}',
            'Content-Type': 'application/json'
        }

        logger.debug(f'Uploading test: url[{url}], headers[{headers}], body[{shortened_json(body)}]')
        response = requests.post(url, data=body, headers=headers)
        if response.status_code != 200:
            logger.error(f'Failed to upload test. Response: {response.text}')
            raise TaukException('failed to upload test results')

        logger.debug(f'Response: {response.text}')
