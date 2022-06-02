"""Helper package to facilitate reporting for webdriver-based tests on Tauk"""
import atexit
import inspect
import logging
import os
import sys
import unittest
from datetime import datetime, timezone
from functools import wraps
from threading import Lock

from tauk.config import TaukConfig
from tauk.context.context import TaukContext
from tauk.enums import AutomationTypes, AttachmentTypes
from tauk.exceptions import TaukException, TaukTestMethodNotFoundException
from tauk.context.test_data import TestCase
from tauk.utils import attach_companion_artifacts, upload_attachments

logger = logging.getLogger('tauk')

mutex = Lock()


class Tauk:
    instance = None
    __context: TaukContext

    def __new__(cls, tauk_config=None):
        """Initialize global instance of Tauk"""
        with mutex:
            if Tauk.instance is None:
                if tauk_config is None:
                    tauk_config = TaukConfig()
                cls.config = tauk_config
                logger.debug(f'Creating new Tauk instance with config [{tauk_config}]')
                cls.instance = super(Tauk, cls).__new__(cls)

                Tauk.__context = TaukContext(tauk_config)

                # Setup atexit handler to clean execution files
                if tauk_config.cleanup_exec_context:
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
    def _get_test_method_details(cls, unittestcase=None, func_name=None, ref_frame=None):
        if unittestcase:
            if not isinstance(unittestcase, unittest.TestCase):
                raise TaukException(
                    f'argument unittestcase ({type(unittestcase)}) is not an instance of unittest.TestCase')

            file_name = inspect.getfile(unittestcase.__class__)
            method_name = unittestcase.id().split('.')[-1]
            return file_name, os.path.relpath(file_name, os.getcwd()), method_name
        elif not func_name and not ref_frame:
            raise TaukException('expecting either function name or reference frame function name')

        found_ref_frame = False
        for i, frame_info in enumerate(inspect.stack()):
            if func_name and func_name in frame_info.frame.f_code.co_names:
                file_name = frame_info.filename
                method_name = func_name
                return file_name, os.path.relpath(file_name, os.getcwd()), method_name
            elif ref_frame and found_ref_frame:
                file_name = frame_info.filename
                method_name = frame_info.function
                return file_name, os.path.relpath(file_name, os.getcwd()), method_name
            elif ref_frame and frame_info.function == ref_frame:
                found_ref_frame = True

        raise TaukTestMethodNotFoundException('failed to find test method details')

    @classmethod
    def destroy(cls):
        if Tauk.is_initialized():
            logger.debug('Destroying Tauk context')

            try:
                if Tauk.__context.companion and Tauk.__context.companion.is_running():
                    Tauk.__context.companion.kill()
            except Exception as ex:
                logger.error('Failed to kill companion app', exc_info=ex)

            try:
                if os.path.exists(Tauk.__context.error_log) and os.path.getsize(Tauk.__context.error_log) > 0:
                    Tauk.__context.api.finish_execution(Tauk.__context.error_log)
                else:
                    Tauk.__context.api.finish_execution()
            except Exception as ex:
                logger.error('Failed report execution complete', exc_info=ex)

            try:
                Tauk.__context.delete_execution_files()
            except Exception as ex:
                logger.error('Failed to delete execution file', exc_info=ex)

            del cls.instance

    @classmethod
    def register_driver(cls, driver, unittestcase=None):
        # Skip registering driver if there is a local variable called tauk_skip
        if hasattr(unittestcase, 'tauk_skip') and unittestcase.tauk_skip is True:
            logger.info(f'Tauk.register_driver: Skipping driver registration for [{unittestcase.id()}]')
            return

        logger.info(f'Registering driver instance: driver=[{driver}], unittestcase=[{unittestcase}]')
        if not Tauk.is_initialized():
            raise TaukException('driver can only be registered from test methods')

        _, relative_file_name, method_name = Tauk._get_test_method_details(
            unittestcase=unittestcase, ref_frame=Tauk.register_driver.__name__)
        test = Tauk._get_testcase(relative_file_name, method_name)
        if test is None:
            raise TaukException(f'TaukListener was not attached to unittest runner')
        test.register_driver(driver, Tauk.__context.companion, relative_file_name, method_name)

    @classmethod
    def observe(cls, custom_test_name=None, excluded=False):
        def inner_decorator(func):
            logger.debug(f'Registering test method=[{func.__name__}]'
                         f' with custom_test_name=[{custom_test_name}], excluded=[{excluded}]')
            test_case = TestCase()
            test_case.custom_name = custom_test_name
            test_case.excluded = excluded
            test_case.method_name = func.__name__

            file_name, relative_file_name, _ = Tauk._get_test_method_details(func_name=test_case.method_name)
            Tauk() if not Tauk.is_initialized() else None
            Tauk.__context.test_data.add_test_case(relative_file_name, test_case)

            @wraps(func)
            def invoke_test_case(*args, **kwargs):
                try:
                    test_case.start_timestamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
                    result = func(*args, **kwargs)
                    test_case.end_timestamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
                    test_case.capture_success_data()
                except Exception:
                    test_case.end_timestamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
                    test_case.capture_failure_data(file_name, sys.exc_info(), func)
                    raise
                else:
                    return result
                finally:
                    if test_case.automation_type == AutomationTypes.APPIUM:
                        try:
                            test_case.capture_appium_logs()
                        except Exception as ex:
                            logger.error('Failed to capture appium server logs', exc_info=ex)

                    # TODO: Investigate about overloaded test name
                    try:
                        json_test_data = Tauk.__context.get_json_test_data(relative_file_name, test_case.method_name)
                        test_case.id = Tauk.__context.api.upload(json_test_data)

                        # Attach companion artifacts
                        attach_companion_artifacts(Tauk.__context.companion, test_case)
                        # Upload attachments
                        upload_attachments(Tauk.__context.api, test_case)
                    except Exception as ex:
                        logger.error(f'Failed to update test results for the test {test_case.method_name}', exc_info=ex)

                    Tauk.__context.test_data.delete_test_case(relative_file_name, test_case.method_name)

            return invoke_test_case

        return inner_decorator

    @classmethod
    def sync_data(cls):
        pass

    @classmethod
    def add_user_data(cls, name, value, unittestcase=None, test_file_name=None, test_method_name=None):
        if hasattr(unittestcase, 'tauk_skip') and unittestcase.tauk_skip is True:
            logger.info(f'Tauk.add_user_data: Skipping user data for [{unittestcase.id()}]')
            return

        if test_file_name and test_method_name:
            test = Tauk._get_testcase(test_file_name, test_method_name)
            if test is None:
                raise TaukException(f'user data can only be added withing the test method,'
                                    f' verify if {test_file_name} has @Tauk.observe decorator')
            test.add_user_data(name, value)
            return

        _, relative_file_name, method_name = Tauk._get_test_method_details(
            unittestcase=unittestcase, ref_frame=Tauk.add_user_data.__name__)
        test = Tauk._get_testcase(relative_file_name, method_name)
        if test is None:
            raise TaukException(f'user data can only be added within testcase')
        test.add_user_data(name, value)

    @classmethod
    def add_attachment(cls, attachment_file_path, attachment_type: AttachmentTypes,
                       unittestcase=None, test_file_name=None, test_method_name=None):
        if hasattr(unittestcase, 'tauk_skip') and unittestcase.tauk_skip is True:
            logger.info(f'Tauk.add_user_data: Skipping user data for [{unittestcase.id()}]')
            return

        if test_file_name and test_method_name:
            test = Tauk._get_testcase(test_file_name, test_method_name)
            if test is None:
                raise TaukException(f'attachment can only be added withing the test method,'
                                    f' verify if {test_file_name} has @Tauk.observe decorator')
            test.add_attachment(attachment_file_path, attachment_type)
            return

        _, relative_file_name, method_name = Tauk._get_test_method_details(
            unittestcase=unittestcase, ref_frame=Tauk.add_user_data.__name__)
        test = Tauk._get_testcase(relative_file_name, method_name)
        if test is None:
            raise TaukException(f'attachment can only be added within testcase')
        test.add_attachment(attachment_file_path, attachment_type)
