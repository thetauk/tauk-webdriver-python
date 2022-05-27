import logging
import re
import subprocess
import responses

from tauk.config import TaukConfig
from tauk.tauk_webdriver import Tauk

logger = logging.getLogger('tauk')

if __name__ == '__main__':
    expected_run_id = '6d917db6-cf5d-4f30-8303-6eefc35e7558'
    responses.RequestsMock()
    responses.start()
    responses.add(responses.POST, re.compile(r'https://www.tauk.com/api/v1/execution/.+/initialize'),
                  json={'run_id': expected_run_id, 'latest_tauk_client_version': '2.0.1'}, status=200)

    try:
        logger.info('Initializing main tauk instance')
        Tauk(TaukConfig('api-token', 'project-id', multiprocess_run=True))

        p1 = subprocess.Popen(['python', 'tests/e2e/listeners/multiprocess/launcher.py',
                               '--test-name=test_one', '--class-name=UnitTestListenerTestOne']
                              )
        p2 = subprocess.Popen(['python', 'tests/e2e/listeners/multiprocess/launcher.py',
                               '--test-name=test_two', '--class-name=UnitTestListenerTestTwo']
                              )
        p1_out, p1_err = p1.communicate()
        print('returncode:', p1.returncode)
        print('out:', p1_out)
        print('err:', p1_err)

        p2_out, p2_err = p2.communicate()
        print('returncode:', p2.returncode)
        print('out:', p2_out)
        print('err:', p2_err)
    finally:
        responses.stop()
