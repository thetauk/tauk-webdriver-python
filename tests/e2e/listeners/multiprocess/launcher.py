import argparse
import importlib
import unittest
from unittest import TestLoader

from tauk.listeners.unittest_multiprocess_listener import TaukMultiprocessListener

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--test-name', type=str)
    parser.add_argument('-c', '--class-name', type=str)
    args = parser.parse_args()

    module = importlib.import_module(f'tests.e2e.listeners.multiprocess.{args.test_name}')
    test_class = getattr(module, args.class_name)
    suite = unittest.TestSuite()
    for test_method in TestLoader().getTestCaseNames(test_class):
        test_instance = test_class(test_method)
        suite.addTest(test_instance)

    unittest.TextTestRunner(resultclass=TaukMultiprocessListener).run(suite)
