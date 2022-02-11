import logging
import time
import unittest

from tauk.listeners.unittest_listener import TaukListener
from tauk.tauk_webdriver import Tauk

logger = logging.getLogger('tauk')


class MyTestCase(unittest.TestCase):
    tauk = Tauk('yvsPoVHuS', '5WOnv-VNsT4O4vSRqNupOXeegpPg')

    @Tauk.observe
    def test_1(self):
        logger.error('This is test_1')
        time.sleep(1)

    @Tauk.observe
    def test_2(self):
        logger.error('This is test_2')
        # tauk = Tauk('test2', '5WOnv-VNsT4O4vSRqNupOXeegpPg')
        self.assertTrue(False, 'test 2 failed assert')
        time.sleep(1)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(resultclass=TaukListener)
    unittest.main(testRunner=runner)
