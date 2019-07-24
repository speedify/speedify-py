import os
import unittest
loader = unittest.TestLoader()
start_dir = os.path.join(os.path.curdir, 'tests')
suite = loader.discover(start_dir)

runner = unittest.TextTestRunner()
runner.run(suite)
