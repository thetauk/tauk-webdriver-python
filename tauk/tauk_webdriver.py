"""Helper package to facilitate reporting for webdriver-based tests on Tauk"""
import inspect
import logging
import sys
import time
import traceback
from threading import Lock

from tauk.enums import TestStatus
from tauk.results import TaukTestResults
from tauk.utils2.requests import RequestUtils
from tauk.utils import print_modified_exception_traceback

logger = logging.getLogger('tauk')

mutex = Lock()


class Tauk:
    _RUN_ID = None

    def __init__(self, api_token, project_id) -> None:
        self._api_token = api_token
        self._project_id = project_id
        # run_id = int(time.time() * 1000000)
        if not Tauk._RUN_ID:
            run_id = RequestUtils.initialize_run(project_id, api_token)
            logger.info(f'[{api_token}] Setting RUN ID: {run_id}')
            with mutex:
                Tauk._RUN_ID = run_id
        else:
            logger.info(f'[{api_token}] Using existing RUN ID: {Tauk._RUN_ID}')
        pass

    @classmethod
    def observe(cls, func):
        all_frames = inspect.stack()
        caller_filename = None
        for frame_info in all_frames:
            if func.__name__ in frame_info.frame.f_code.co_names:
                caller_filename = frame_info.filename
                break

        def invoke_test_case(*args, **kwargs):
            test_result = TaukTestResults(test_name=func.__name__, test_file_name=caller_filename)

            try:
                test_result.test_start_time = time.time()
                result = func(*args, **kwargs)
                test_result.test_end_time = time.time()
                test_result.test_status = TestStatus.PASSED.value
            except:
                test_result.test_end_time = time.time()
                test_result.test_status = TestStatus.FAILED.value

                exc_type, exc_value, exc_traceback = sys.exc_info()
                stack_summary_list = traceback.extract_tb(exc_traceback)
                filename, line_number, invoked_func, code_executed = None, None, None, None
                for stack_trace in stack_summary_list:
                    if stack_trace.filename == caller_filename:
                        filename, line_number, invoked_func, code_executed = stack_trace
                        break

                test_result.error = (exc_value, line_number, invoked_func, code_executed)

                # Suppress the traceback information
                # (only the exception type and value will be printed)
                # and print our custom traceback information
                print_modified_exception_traceback(exc_type, exc_value, exc_traceback, tauk_package_filename=__file__)
                sys.tracebacklimit = 0
                raise
            finally:
                logger.info(test_result.to_json())

        return invoke_test_case
