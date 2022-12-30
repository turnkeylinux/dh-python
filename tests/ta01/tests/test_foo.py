import os
import unittest

class TestPybuildAutopkgtest(unittest.TestCase):

    def test_pass_or_fails(self):
        self.assertIsNone(os.environ.get("FAILS"))
