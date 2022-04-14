import unittest

from tauk.exceptions import TaukException


class UnitTestListenerTestTwo(unittest.TestCase):
    def test_two(self):
        print('running test two')
        self.assertEqual(True, True, 'failed to assert')  # add assertion here
        # raise TaukException('simple test error')
