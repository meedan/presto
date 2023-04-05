import unittest

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.discover('test', pattern='*_test.py')
    runner = unittest.TextTestRunner()
    result = runner.run(suite)