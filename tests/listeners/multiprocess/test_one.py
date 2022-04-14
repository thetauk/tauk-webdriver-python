import unittest

from tauk.exceptions import TaukException


class UnitTestListenerTestOne(unittest.TestCase):
    def test_one(self):
        print('running test one')
        self.assertEqual(True, False, 'failed to assert')  # add assertion here
        # raise TaukException('simple test error')
