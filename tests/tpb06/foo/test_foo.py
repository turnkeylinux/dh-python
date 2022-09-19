import os
from unittest import TestCase
import subprocess


class RequiredTest(TestCase):
    def test_tests_are_executed(self):
        open('test-executed', 'w').close()

    def test_entry_point_executed(self):
        path, _, __ = os.environ['PATH'].partition(":")
        assert "scripts" in path
        subprocess.run('foo', check=True)
