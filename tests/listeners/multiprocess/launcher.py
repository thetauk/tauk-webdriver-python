import re
import unittest

import responses

from tauk.listeners.unittest_multiprocess_listener import TaukMultiprocessListener
from tauk.tauk_webdriver import Tauk
from tests.listeners.multiprocess.test_one import UnitTestListenerTestOne
from tests.listeners.multiprocess.test_two import UnitTestListenerTestTwo

if __name__ == '__main__':
    expected_run_id = '6d917db6-cf5d-4f30-8303-6eefc35e7558'
    responses.RequestsMock()
    responses.start()
    responses.add(responses.POST, re.compile(r'https://www.tauk.com/api/v1/execution/.+/initialize'),
                  json={'run_id': expected_run_id, 'latest_tauk_client_version': '2.0.1'}, status=200)
    responses.add(responses.POST, re.compile(r'https://www.tauk.com/api/v1/execution/.+/.+/report/upload'),
                  json={'message': 'success'}, status=200)

    Tauk(api_token='api-token', project_id='project-id', multi_process_run=True)

    # runner = unittest.TextTestRunner(verbosity=0, failfast=True, resultclass=TaukListener)
    # runner.run(suite)
    suite = unittest.TestSuite()
    suite.addTest(UnitTestListenerTestOne('test_one'))
    suite.addTest(UnitTestListenerTestTwo('test_two'))
    unittest.TextTestRunner(resultclass=TaukMultiprocessListener).run(suite)

    responses.stop()
