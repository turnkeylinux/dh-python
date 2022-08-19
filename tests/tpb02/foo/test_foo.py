from unittest import TestCase


class RequiredTest(TestCase):
    def test_tests_are_executed(self):
        open('test-executed', 'w').close()

    def test_testfiles_exist(self):
        open('testfile1.txt').close()
        open('testfile2.txt').close()
        open('testdir/testfile3.txt').close()
