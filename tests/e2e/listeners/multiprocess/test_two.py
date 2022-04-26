import time
import unittest

from tauk.exceptions import TaukException
from tests.utils import mock_success


class UnitTestListenerTestTwo(unittest.TestCase):
    @mock_success(multiprocess=True)
    def test_two(self):
        print('running test two')
        self.assertEqual(True, True, 'failed to assert')  # add assertion here
        # raise TaukException('simple test error')
