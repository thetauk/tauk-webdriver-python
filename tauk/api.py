import logging
import time

import requests

logger = logging.getLogger('tauk')


def post(url, payload, headers):
    return requests.post(
        url,
        json=payload,
        headers=headers
    )


class TaukApi:
    _API_URL = 'http://localhost:5000/api/v1'

    # _API_URL = 'https://requestinspector.com/inspect/01fvhhd8vg2sfd6hpn3c77rd7e'

    @staticmethod
    def initialize_run_mock(api_token, project_id):
        return 'runid-dfg'

    @staticmethod
    def initialize_run(api_token, project_id):
        url = f'${TaukApi._API_URL}/execution/${project_id}/initialize'
        body = {
            'timestamp': round(int(time.time() * 1000))
        }

        headers = {
            'Authorization': f'Bearer {api_token}'
        }

        r = post(url, body, headers)
        logger.info(f'Response: {r.json()}')
        # TODO: Validate response code
        return r.json()['run_id']

    @staticmethod
    def test_start(api_token, project_id, run_id, test_name, file_name, start_time):
        url = f'${TaukApi._API_URL}/api/v1/execution/${project_id}/${run_id}/report/test/start'
        body = {
            'test_name': test_name,
            'file_name': file_name,
            'start_time': start_time,
        }

        headers = {
            'Authorization': f'Bearer {api_token}'
        }

        r = post(url, body, headers)
        logger.info(f'Response: {r.json()}')
        # TODO: Validate response code
        return r.json()['test_id']

    @staticmethod
    def test_finish(api_token, project_id, run_id, test_name, file_name, start_time, end_time):
        url = f'${TaukApi._API_URL}/api/v1/execution/${project_id}/${run_id}/report/test/finish'
        body = {
            'test_name': test_name,
            'file_name': file_name,
            'start_time': start_time,
            'end_time': end_time,
        }

        headers = {
            'Authorization': f'Bearer {api_token}'
        }

        r = post(url, body, headers)
        logger.info(f'Response: {r.json()}')
        # TODO: Validate response code
        return r.json()['test_id']

    @staticmethod
    def upload(api_token, project_id, run_id, test_name, file_name, start_time):
        url = f'${TaukApi._API_URL}/api/v1/execution/${project_id}/${run_id}/report/upload'
        body = {
            'test_name': test_name,
            'file_name': file_name,
            'start_time': start_time,
            'run_id': run_id
        }

        headers = {
            'Authorization': f'Bearer {api_token}'
        }

        r = post(url, body, headers)
        logger.info(f'Response: {r.json()}')
        # TODO: Validate response code
        return r.json()['test_id']
