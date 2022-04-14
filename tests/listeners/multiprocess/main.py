import re
import subprocess

import responses

from tauk.tauk_webdriver import Tauk

if __name__ == '__main__':
    expected_run_id = '6d917db6-cf5d-4f30-8303-6eefc35e7558'
    responses.RequestsMock()
    responses.start()
    responses.add(responses.POST, re.compile(r'https://www.tauk.com/api/v1/execution/.+/initialize'),
                  json={'run_id': expected_run_id, 'latest_tauk_client_version': '2.0.1'}, status=200)

    try:
        Tauk(api_token='api-token', project_id='project-id', multi_process_run=True)

        p1 = subprocess.run(['python', 'tests/listeners/multiprocess/launcher.py',
                             '--test-name=test_one', '--class-name=UnitTestListenerTestOne']
                            )
        print('returncode', p1.returncode)
    finally:
        responses.stop()
