import unittest

class TestThatWeDontRunTheseTests(unittest.TestCase):

    def test_fail(self):
        # We want the custom test runner to run, not this test suite
        self.assertTrue(False)
