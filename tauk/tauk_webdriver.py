"""Helper package to facilitate reporting for webdriver-based tests on Tauk"""
import atexit
import inspect
import logging
import os
import sys
from datetime import datetime, timezone
from functools import wraps
from threading import Lock

from tauk.context.context import TaukContext
from tauk.exceptions import TaukException
from tauk.context.test_data import TestCase

logger = logging.getLogger('tauk')

mutex = Lock()


class Tauk:
    instance = None
    __context: TaukContext

    # TODO: Add documentation
    def __new__(cls, api_token=None, project_id=None, multi_process_run=False, cleanup_exec_context=True):
        with mutex:
            if Tauk.instance is None:
                logger.debug(f'Creating new Tauk instance with api_token={api_token}, project_id={project_id}, '
                             f'multi_process_run={multi_process_run}')
                cls.instance = super(Tauk, cls).__new__(cls)
                if not api_token or not project_id:
                    logger.info('Looking for API token and project ID in environment variables')
                    api_token = os.getenv('TAUK_API_TOKEN')
                    project_id = os.getenv('TAUK_PROJECT_ID')
                    multi_process_run = os.getenv('TAUK_MULTI_PROCESS',
                                                  f'{multi_process_run}').lower().strip() == "true"

                if not multi_process_run and (not api_token or not project_id):
                    raise TaukException('Please ensure that a valid TAUK_API_TOKEN and TAUK_PROJECT_ID is set')
                Tauk.__context = TaukContext(api_token, project_id, multi_process_run=multi_process_run)

                if multi_process_run and cleanup_exec_context:
                    atexit.register(Tauk.destroy)

            return cls.instance

    @classmethod
    def is_initialized(cls):
        return False if Tauk.instance is None else True

    @classmethod
    def get_instance(cls):
        if Tauk.instance is None:
            raise Exception('Tauk is not yet initialized')
        logger.info(f'Returning Tauk instance {cls.instance}')
        return cls.instance

    @classmethod
    def get_context(cls):
        return Tauk.__context

    @classmethod
    def _get_testcase(cls, file_name, test_name):
        test_suite = Tauk.__context.test_data.get_test_suite(file_name)
        if test_suite is None:
            return None
        test_case = test_suite.get_test_case(test_name)
        if test_case is None:
            return None
        return test_case

    @classmethod
    def destroy(cls):
        if Tauk.is_initialized():
            logger.debug('Destroying Tauk context')
            Tauk.__context.delete_execution_files()
            del cls.instance

    # TODO: Move identifier to unique method
    @classmethod
    def register_driver(cls, driver, test_filename=None, test_method_name=None):
        logger.info(f'Registering driver instance: '
                    f'driver=[{driver}], test_file_name=[{test_filename}], test_method_name=[{test_method_name}]')

        if not Tauk.is_initialized():
            raise TaukException('driver can only be registered from test methods')

        caller_frame_records = inspect.stack()
        register_driver_stack_index = 0
        found_register_driver = False

        if test_filename and test_method_name:
            test = Tauk._get_testcase(test_filename, test_method_name)
            if test is None:
                raise TaukException(f'driver can only be registered for observed methods.'
                                    f' Verify if {test_filename} has @Tauk.observe decorator')
            test.register_driver(driver)
            return

        for i, frame_info in enumerate(caller_frame_records):
            # We pick the next frame after register driver
            if found_register_driver:
                test_filename = frame_info.filename
                test_relative_file_name = test_filename.replace(f'{os.getcwd()}{os.sep}', '')
                test_method_name = frame_info.function
                test = Tauk._get_testcase(test_relative_file_name, test_method_name)
                if test is None:
                    raise TaukException(
                        f'driver can only be registered with an active tauk listener or an observed method')
                test.register_driver(driver, test_filename, test_method_name)
                return

            if frame_info.function == 'register_driver':
                found_register_driver = True
                register_driver_stack_index = i

        raise TaukException(f'driver(2) can only be registered with an active tauk listener or an observed method')

    @classmethod
    def observe(cls, custom_test_name=None, excluded=False):

        def inner_decorator(func):
            logger.debug(f'Registering test method=[{func.__name__}]'
                         f' with custom_test_name=[{custom_test_name}], excluded=[{excluded}]')
            test_case = TestCase()
            test_case.custom_name = custom_test_name
            test_case.excluded = excluded

            all_frames = inspect.stack()
            caller_filename = None
            caller_relative_filename = None
            for frame_info in all_frames:
                if func.__name__ in frame_info.frame.f_code.co_names:
                    caller_filename = frame_info.filename
                    caller_relative_filename = caller_filename.replace(f'{os.getcwd()}{os.sep}', '')
                    test_case.method_name = func.__name__
                    Tauk() if not Tauk.is_initialized() else None
                    Tauk.__context.test_data.add_test_case(caller_relative_filename, test_case)
                    break

            @wraps(func)
            def invoke_test_case(*args, **kwargs):
                try:
                    test_case.start_timestamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
                    result = func(*args, **kwargs)
                    test_case.end_timestamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
                    test_case.capture_success_data()
                except:
                    test_case.end_timestamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
                    test_case.capture_failure_data()
                    error_line_number = test_case.capture_error(caller_filename, sys.exc_info())
                    test_case.capture_test_steps(testcase=func, error_line_number=error_line_number)

                    # TODO: cleanup stack track here
                    raise
                else:
                    return result
                finally:
                    test_case.capture_appium_logs()
                    # TODO: Investigate about overloaded test name
                    Tauk.__context.api.upload(
                        Tauk.__context.get_json_test_data(caller_relative_filename, test_case.method_name))

            return invoke_test_case

        return inner_decorator

    @classmethod
    def sync_data(cls):
        pass

    @classmethod
    def add_user_data(cls, name, value, test_file_name=None, test_method_name=None):
        if test_file_name and test_method_name:
            test = Tauk._get_testcase(test_file_name, test_method_name)
            if test is None:
                raise TaukException(f'user data can only be added withing the test method'
                                    f' Verify if {test_file_name} has @Tauk.observe decorator')
            test.add_user_data(name, value)
            return

        caller_frame_records = inspect.stack()
        found_register_driver = False

        for i, frame_info in enumerate(caller_frame_records):
            # We pick the next frame after register driver
            logger.info(f'[{i}] Checking function: {frame_info.function}')
            if found_register_driver:
                test_file_name = frame_info.filename.replace(os.getcwd(), '')
                test_method_name = frame_info.function
                logger.info(f'[{i}] Found: {test_file_name}, {test_method_name}')
                test = Tauk._get_testcase(test_file_name, test_method_name)
                if test is None:
                    raise TaukException(f'Driver can only be registered for observed methods.'
                                        f' Verify if {test_file_name} has @Tauk.observe decorator')
                test.add_user_data(name, value)
                return

            if frame_info.function == 'register_driver':
                found_register_driver = True
                register_driver_stack_index = i

        raise TaukException(f'Driver can only be registered for observed methods.'
                            f' Verify if {test_file_name} has @Tauk.observe decorator')
