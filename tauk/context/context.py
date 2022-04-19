import hashlib
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

    def __init__(self, api_token, project_id, multi_process_run=False):
        self.test_data: TestData = TestData()
        self.exec_dir = os.path.join(os.environ.get('TAUK_HOME'), hashlib.md5(os.getcwd().encode()).hexdigest())
        self.exec_file = os.path.join(self.exec_dir, 'exec.run')
        self.api = TaukApi(api_token, project_id, multi_process_run)

        if multi_process_run:
            self._setup_execution_file()
            return
        else:
            self.delete_execution_files()

        self.run_id = self._init_run()
        logger.info(f'[{api_token}] Setting RUN ID: {self.run_id}')

    def _init_run(self, run_id=None):
        # return self.api.initialize_run_mock(self.test_data, run_id)
        return self.api.initialize_run(self.test_data, run_id)

    def delete_execution_files(self):
        if not os.path.exists(self.exec_dir):
            return

        logger.debug(f'Deleting execution files in {self.exec_dir}')
        lock_file = f'{self.exec_file}.lock'
        if os.path.exists(self.exec_file):
            os.remove(self.exec_file)
        if os.path.exists(lock_file):
            os.remove(lock_file)
        os.rmdir(self.exec_dir)

    def _setup_execution_file(self):
        logger.debug(f'Setting up execution file {self.exec_file}')

        def set_exec_file(r_id, a_token, p_id):
            with open(self.exec_file, "w") as f:
                logger.debug(f'Updating execution file with {r_id}')
                f.write(f'{r_id},{a_token},{p_id}')
                self.run_id = r_id

        def is_valid_uuid(value):
            try:
                uuid.UUID(value)
                return True
            except ValueError:
                return False

        if not os.path.exists(self.exec_dir):
            os.makedirs(self.exec_dir)

        with FileLock(f'{self.exec_file}.lock', timeout=30):
            if os.path.exists(self.exec_file):
                with open(self.exec_file, 'r') as file:
                    run_id, api_token, project_id = file.read().strip().split(',')
                    self.api.set_token(api_token, project_id)
                    if is_valid_uuid(run_id):
                        new_run_id = self._init_run(run_id)
                        if new_run_id != run_id:
                            logger.debug(f'Existing runID [{run_id}] is invalid')
                            set_exec_file(new_run_id, api_token, project_id)
                        return
                    else:
                        logger.warning(f'Invalid runID [{run_id}]')

            set_exec_file(self._init_run(), self.api.get_api_token(), self.api.get_project_id())

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
