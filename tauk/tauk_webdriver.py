"""Helper package to facilitate reporting for webdriver-based tests on Tauk"""
import inspect
import logging
import sys
import time
import traceback
from threading import Lock

from tauk.context import TaukContext
from tauk.enums import TestStatus
from tauk.exceptions import TaukException
from tauk.results import TaukTestResults
from tauk.test_data import TestCase
from tauk.utils import print_modified_exception_traceback

logger = logging.getLogger('tauk')

mutex = Lock()


class Tauk:
    __context: TaukContext

    def __new__(cls, api_token, project_id):
        with mutex:
            if not hasattr(cls, 'instance'):
                cls.instance = super(Tauk, cls).__new__(cls)
                Tauk.__context = TaukContext(api_token, project_id)

            return cls.instance

    @classmethod
    def get_instance(cls):
        if not hasattr(cls, 'instance'):
            raise Exception('Tauk is not yet initialized')
        logger.info(f'Returning Tauk instance {cls.instance}')
        return cls.instance

    @classmethod
    def debug_print(cls):
        Tauk.__context.print()

    @classmethod
    def observe2(cls, func=None, *, custom_test_name=None):
        pass

    @classmethod
    def register_driver(cls, driver, test_file_name=None, test_method_name=None):
        logger.info(
            f'Registering driver instance: driver {driver}, test_file_name={test_file_name}, test_method_name={test_method_name}')
        caller_frame_records = inspect.stack()
        register_driver_stack_index = 0
        found_register_driver = False

        def locate_testcase(file_name, test_name):
            test_suite = Tauk.__context.test_data.get_test_suite(file_name)
            if test_suite is None:
                return None
            test_case = test_suite.get_test_case(test_name)
            if test_case is None:
                return None
            return test_case

        if test_file_name and test_method_name:
            test = locate_testcase(test_file_name, test_method_name)
            if test is None:
                raise TaukException(f'Driver can only be registered for observed methods.'
                                    f' Verify if {test_file_name} has @Tauk.observe decorator')
            test.register_driver(driver)
            return

        for i, frame_info in enumerate(caller_frame_records):
            # We pick the next frame after register driver
            logger.info(f'[{i}] Checking function: {frame_info.function}')
            if found_register_driver:
                test_file_name = frame_info.filename
                test_method_name = frame_info.function
                logger.info(f'[{i}] Found: {test_file_name}, {test_method_name}')
                test = locate_testcase(test_file_name, test_method_name)
                if test is None:
                    raise TaukException(f'Driver can only be registered for observed methods.'
                                        f' Verify if {test_file_name} has @Tauk.observe decorator')
                test.register_driver(driver)
                return

            if frame_info.function == 'register_driver':
                found_register_driver = True
                register_driver_stack_index = i

        raise TaukException(f'Driver can only be registered for observed methods.'
                            f' Verify if {test_file_name} has @Tauk.observe decorator')

    @classmethod
    def observe(cls, test_name=None, excluded=False):
        print(f'test_name: {test_name}')

        def inner_decorator(func):
            testcase = TestCase()

            all_frames = inspect.stack()
            caller_filename = None
            for frame_info in all_frames:
                if func.__name__ in frame_info.frame.f_code.co_names:
                    caller_filename = frame_info.filename
                    testcase.name = func.__name__
                    Tauk(api_token='sssdf', project_id='dsf')
                    Tauk.__context.test_data.add_test_case(caller_filename, testcase)
                    break

            def invoke_test_case(*args, **kwargs):
                test_result = TaukTestResults(test_name=func.__name__, test_file_name=caller_filename)

                try:
                    testcase.start_time = time.time()
                    result = func(*args, **kwargs)
                    testcase.end_time = time.time()
                    testcase.capture_success_data()
                except:
                    testcase.end_time = time.time()
                    testcase.capture_failure_data()
                    testcase.capture_error(caller_filename, sys.exc_info())

                    raise
                else:
                    return result
                finally:
                    Tauk.debug_print()

            return invoke_test_case

        return inner_decorator
