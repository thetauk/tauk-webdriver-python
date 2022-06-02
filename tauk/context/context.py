import hashlib
import logging
import os
import shutil
import uuid
import jsonpickle

from tauk.api import TaukApi
from tauk.companion.companion import TaukCompanion
from tauk.config import TaukConfig
from tauk.context.test_data import TestData
from tauk.exceptions import TaukException
from tauk.log_formatter import CustomJsonFormatter

from filelock import FileLock

logger = logging.getLogger('tauk')


class TaukContext:

    def __init__(self, tauk_config: TaukConfig):
        self.test_data: TestData = TestData()
        self._setup_exec_dir(tauk_config.multiprocess_run)
        self._setup_error_logger()
        self._exec_file = os.path.join(self.exec_dir, 'exec.run')
        self.api = TaukApi(tauk_config.api_token, tauk_config.project_id, tauk_config.multiprocess_run)

        # Initialize Tauk Companion
        self.companion: TaukCompanion | None = None
        if tauk_config.is_companion_enabled():
            self.companion = TaukCompanion(tauk_config.api_token, self.exec_dir, tauk_config.companion_config)
            try:
                self.companion.launch()
            except Exception as ex:
                logger.error('Failed to launch tauk companion', exc_info=ex)

        if tauk_config.multiprocess_run:
            self._setup_execution_file()
            return

        self.run_id = self._init_run()

    def _setup_exec_dir(self, multiprocess_run):
        self.exec_dir = self._get_exec_dir(multiprocess_run)
        if not os.path.exists(self.exec_dir):
            os.makedirs(self.exec_dir)
        elif not multiprocess_run:
            # If execution dir already exists, and it's not a multiprocess run we have to delete it
            logger.warning(f'Execution dir {self.exec_dir} already exists for non multiprocess run, hence deleting it')
            shutil.rmtree(self.exec_dir)
            # Create the execution dir again so that it's empty now
            os.makedirs(self.exec_dir)

    def _setup_error_logger(self):
        self.error_log = os.path.join(self.exec_dir, 'tauk-webdriver-error.log')
        error_file_handler = logging.FileHandler(filename=self.error_log)
        error_file_handler.setLevel(logging.WARNING)
        formatter = CustomJsonFormatter('%(timestamp)s %(process)d %(threadName)s %(levelname)s %(message)s')
        error_file_handler.setFormatter(formatter)
        logger.addHandler(error_file_handler)

    def _get_exec_dir(self, multi_process_run=False):
        if os.environ.get('TAUK_EXEC_DIR'):
            logger.debug(f'Using execution dir found in environment variable {os.environ.get("TAUK_EXEC_DIR")}')
            return os.environ.get('TAUK_EXEC_DIR')

        exec_home = os.path.join(os.environ.get('TAUK_HOME'), hashlib.md5(os.getcwd().encode()).hexdigest())

        if not multi_process_run:
            # Still use pid because multiple instances of the project can be launched
            exec_dir = os.path.join(exec_home, f'{os.getppid()}')
            logger.debug(f'Using execution dir at {exec_dir}')
            return exec_dir

        parent_exec_dir = os.path.join(exec_home, f'{os.getppid()}')
        if os.path.exists(parent_exec_dir):
            logger.debug(f'Found existing execution dir at {parent_exec_dir}')
            return parent_exec_dir

        new_exec_dir = os.path.join(exec_home, f'{os.getpid()}')
        logger.debug(f'Using new execution dir at {new_exec_dir}')
        # Set environment variable so that child process can use this
        os.environ['TAUK_EXEC_DIR'] = new_exec_dir
        return new_exec_dir

    def _init_run(self, run_id=None):
        return self.api.initialize_run(self.test_data, run_id)

    def delete_execution_files(self):
        if not os.path.exists(self.exec_dir):
            return

        logger.debug(f'Deleting execution files in {self.exec_dir}')
        # Delete exec file
        lock_file = f'{self._exec_file}.lock'
        if os.path.exists(self._exec_file):
            os.remove(self._exec_file)
        # Delete exec lock file
        if os.path.exists(lock_file):
            os.remove(lock_file)

        # Delete error log file
        if os.path.exists(self.error_log):
            os.remove(self.error_log)

        # Delete companion dir
        companion_dir = os.path.join(self.exec_dir, 'companion')
        if os.path.exists(companion_dir):
            shutil.rmtree(companion_dir)

        os.rmdir(self.exec_dir)

    def _setup_execution_file(self):
        def set_exec_file(r_id, a_token, p_id):
            with open(self._exec_file, "w") as f:
                logger.debug(f'Updating execution file with {r_id}')
                f.write(f'{r_id},{a_token},{p_id}')
                self.run_id = r_id

        def is_valid_uuid(value):
            try:
                uuid.UUID(value)
                return True
            except ValueError:
                return False

        with FileLock(f'{self._exec_file}.lock', timeout=30):
            logger.debug(f'Execution locked for {self._exec_file}')
            if os.path.exists(self._exec_file):
                with open(self._exec_file, 'r') as file:
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
            logger.debug(f'Execution unlocked for {self._exec_file}')

    def get_json_test_data(self, test_suite_filename, test_method_name):
        suite = self.test_data.get_test_suite(test_suite_filename)
        if not suite:
            raise TaukException(f'Could not find suite with filename {test_suite_filename}')

        suite_json = suite.to_json()

        # Clean up tests
        for test in suite_json.get('test_cases'):
            if test.get('method_name') != test_method_name:
                suite_json.get('test_cases').remove(test)

        json_data = {
            "test_suites": [
                suite_json
            ]
        }

        return jsonpickle.encode(json_data, unpicklable=False)
