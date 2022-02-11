import logging

import requests

logger = logging.getLogger('tauk')


class RequestUtils:
    _API_URL = 'http://localhost:5000/api/v1/run/initialize'
    # _API_URL = 'https://requestinspector.com/inspect/01fvhhd8vg2sfd6hpn3c77rd7e'

    @staticmethod
    def post(url, payload, headers):
        return requests.post(
            url,
            json=payload,
            headers=headers
        )

    @staticmethod
    def initialize_run(api_token, project_id):
        r = RequestUtils.post(RequestUtils._API_URL, {"project_id": project_id}, {"api_token": api_token})
        logger.info(f'Response: {r.json()}')
        # TODO: Validate response code
        return r.json()['run_id']
