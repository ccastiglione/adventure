from unittest import TestCase
from result import *


class TestResult(TestCase):

    def test_eq_success(self):
        r = Result("foo", True)
        q = Result("foo", True)
        self.assertTrue(r == q)

    def test_eq_fail1(self):
        r = Result("foo", True)
        q = Result("bar", True)
        self.assertFalse(r == q)

    def test_eq_fail2(self):
        r = Result("foo", True)
        q = Result("foo", False)
        self.assertFalse(r == q)

    def test_append(self):
        r = Result("foo", True)
        r.append("bar")
        self.assertEqual(r,Result("foobar", True))

    def test_success(self):
        r = Success("foo")
        self.assertTrue(r.success)

    def test_failure(self):
        r = Failure("foo")
        self.assertFalse(r.success)
