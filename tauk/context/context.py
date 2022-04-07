import logging
import copy
import os
import uuid

import jsonpickle

from tauk.api import TaukApi
from tauk.context.test_data import TestData
from tauk.exceptions import TaukException
from filelock import FileLock

logger = logging.getLogger('tauk')


class TaukContext:
    test_data: TestData = TestData()
    run_id: str
    api: TaukApi

    def __init__(self, api_token, project_id, multi_process_run=False):
        self.api = TaukApi(api_token, project_id, multi_process_run)
        if multi_process_run:
            self._setup_execution_file()
            return
        else:
            exec_file = os.path.join(os.environ['TAUK_HOME'], 'exec.run')
            lock_file = f'{exec_file}.lock'
            if os.path.exists(exec_file):
                os.remove(exec_file)
            if os.path.exists(lock_file):
                os.remove(lock_file)

        self.run_id = self._init_run()
        # TODO: implement warning for newer tauk client
        logger.info(f'[{api_token}] Setting RUN ID: {self.run_id}')

    def _init_run(self, run_id=None):
        # return self.api.initialize_run_mock(self.test_data, run_id)
        return self.api.initialize_run(self.test_data, run_id)

    def _setup_execution_file(self):
        exec_file = os.path.join(os.environ['TAUK_HOME'], 'exec.run')
        logger.debug(f'Setting up execution file {exec_file}')

        def set_exec_file(r_id):
            with open(exec_file, "w") as f:
                logger.debug(f'Updating execution file with {r_id}')
                f.write(r_id)
                self.run_id = r_id

        def is_valid_uuid(value):
            try:
                uuid.UUID(value)
                return True
            except ValueError:
                return False

        if os.path.exists(exec_file):
            with FileLock(f'{exec_file}.lock', timeout=30):
                with open(exec_file, 'r') as file:
                    run_id = file.read().strip()
                    if is_valid_uuid(run_id):
                        new_run_id = self._init_run(run_id)
                        if new_run_id != run_id:
                            logger.debug(f'Existing runID [{run_id}] is invalid')
                            set_exec_file(new_run_id)
                        return
                    else:
                        logger.warning(f'Invalid runID [{run_id}]')

        set_exec_file(self._init_run())

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

        return jsonpickle.encode(json_data, unpicklable=False)
