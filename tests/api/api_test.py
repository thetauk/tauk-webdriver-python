import unittest
import responses

from tauk.api import TaukApi


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    @responses.activate
    def test_something(self):
        responses.add(responses.POST, TaukApi._API_URL,
                      json={'run_id': 'sdfasdfsdaf'}, status=404)

        run_id = TaukApi.initialize_run(api_token='sdfs', project_id='sdf')
        self.assertEqual(run_id, 'sdfasdfsdaf')  # add assertion here


    def test_something_else(self):
        pass


if __name__ == '__main__':

    unittest.main()
