import logging
import copy

import jsonpickle

from tauk.api import TaukApi
from tauk.context.test_data import TestData
from tauk.exceptions import TaukException

logger = logging.getLogger('tauk')


class TaukContext:
    test_data: TestData = TestData()
    run_id: str
    api: TaukApi

    def __init__(self, api_token, project_id) -> None:
        self.api = TaukApi(api_token, project_id)
        # self.run_id = self.api.initialize_run_mock(self.test_data)
        self.run_id = self.api.initialize_run(self.test_data)
        logger.info(f'[{api_token}] Setting RUN ID: {self.run_id}')

    def print(self):
        print('-------- Test Data ---------------')
        print(jsonpickle.encode(self.test_data, unpicklable=False, indent=3))
        print('-------- Test Data ---------------')

    def get_json_test_data(self, test_suite_filename, test_method_name):
        suite = self.test_data.get_test_suite(test_suite_filename)
        if not suite:
            raise TaukException(f'Could not find suite with filename {test_suite_filename}')

        suite_copy = copy.deepcopy(suite)
        # Clean up tests
        for test in suite_copy.test_cases:
            if test.method_name != test_method_name:
                suite_copy.test_cases.remove(test)

        json_data = {
            "test_suites": [
                suite_copy
            ]
        }

        return jsonpickle.encode(json_data, unpicklable=False, indent=3)
