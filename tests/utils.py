import inspect
import os
import typing

import responses

from tauk.exceptions import TaukException
from tauk.tauk_webdriver import Tauk


def mock(urls: typing.List[str], json_responses: typing.List[object], statuses: typing.List[int], validation=None):
    if not isinstance(urls, list) or not isinstance(json_responses, list) or not isinstance(statuses, list):
        raise TaukException('arguments to mock method must be of list type of same size')

    if not (len(urls) == len(json_responses) == len(statuses)):
        raise TaukException('arguments to mock method must be of list type of same size')

    responses.RequestsMock()
    responses.start()

    for i, url in enumerate(urls):
        responses.add(responses.POST, url, json=json_responses[i], status=statuses[i])

    api_token = os.getenv('TAUK_API_TOKEN', 'api-token')
    project_id = os.getenv('TAUK_PROJECT_ID', 'project-id')
    Tauk(api_token=api_token, project_id=project_id)

    def inner_decorator(func):
        caller_filename = None
        test_method_name = None
        for frame_info in inspect.stack():
            if all(elem in frame_info.frame.f_code.co_names for elem in ['Tauk', 'observe']):
                caller_filename = frame_info.filename.replace(f'{os.getcwd()}{os.sep}', '')
                test_method_name = frame_info.frame.f_code.co_names[-1]
                break

        def inner(*args, **kwargs):
            try:
                result = func(*args, **kwargs)

                if callable(result):
                    ctx = Tauk().get_context()
                    test_data = ctx.test_data
                    test_suite = test_data.get_test_suite(caller_filename)
                    if test_suite:
                        test_case = test_suite.get_test_case(test_method_name)
                        if test_case:
                            result(caller_filename, test_method_name, ctx, test_data, test_suite, test_case)

                return result
            except:
                if validation and callable(validation):
                    ctx = Tauk().get_context()
                    test_data = ctx.test_data
                    test_suite = test_data.get_test_suite(caller_filename)
                    if test_suite:
                        test_case = test_suite.get_test_case(test_method_name)
                        if test_case:
                            validation(caller_filename, test_method_name, ctx, test_data, test_suite, test_case)
            finally:
                responses.stop()

        return inner

    return inner_decorator


def mock_success(expected_run_id='6d917db6-cf5d-4f30-8303-6eefc35e7558', validation=None):
    return mock(
        urls=[
            f'https://www.tauk.com/api/v1/execution/project-id/initialize',
            f'https://www.tauk.com/api/v1/execution/project-id/{expected_run_id}/report/upload'
        ],
        json_responses=[
            {'run_id': expected_run_id, 'message': 'success'},
            {'message': 'success'}
        ],
        statuses=[200, 200],
        validation=validation
    )
