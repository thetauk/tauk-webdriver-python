import logging
from tauk.api import TaukApi
from tauk.test_data import TestData

logger = logging.getLogger('tauk')


class TaukContext:
    test_data: TestData = TestData()
    _run_id: str

    def __init__(self, api_token, project_id) -> None:
        self._api_token = api_token
        self._project_id = project_id
        self._run_id = TaukApi.initialize_run_mock(project_id, api_token)
        # self._run_id = TaukApi.initialize_run(project_id, api_token)
        logger.info(f'[{api_token}] Setting RUN ID: {self._run_id}')

    def print(self):
        print('-------- Test Data ---------------')
        print(f'run_id: {self._run_id}')
        self.test_data.print()
        print('-------- Test Data ---------------')
