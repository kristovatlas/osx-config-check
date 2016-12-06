"""Unit tests for semver_check.py"""

import unittest
from .. import semver_check #semver_check.py

class SemVerTest(unittest.TestCase):
    """Tests the script"""
    def setUp(self):
        print "Running Semantic Version Check Test..."

    def tearDown(self):
        pass

    def test_git_version_equal(self):
        """Do simple match"""
        stdin = ("git version 2.10.2", "")
        semver = "2.10.2"
        args = {'semver': semver}
        self.assertTrue(semver_check.is_match(stdin=stdin, args=args))

    def test_git_version_not_equal(self):
        """Do simple mis-match"""
        stdin = ("git version 2.10.2", "")
        semver = "2.10.3"
        args = {'semver': semver}
        self.assertFalse(semver_check.is_match(stdin=stdin, args=args))

    def test_git_version_ge(self):
        """Simple match with GE operator."""
        stdin = ("git version 2.10.2", "")
        semver = ">=2.10.2"
        args = {'semver': semver}
        self.assertTrue(semver_check.is_match(stdin=stdin, args=args))

    def test_git_version_too_old(self):
        """Simple mis-match with GE operator."""
        stdin = ("git version 2.10.2", "")
        semver = ">=2.10.3"
        args = {'semver': semver}
        self.assertFalse(semver_check.is_match(stdin=stdin, args=args))

    def test_git_version_greater_than(self):
        """Simple match with GE operator."""
        stdin = ("git version 2.10.2", "")
        semver = ">=2.9.9"
        args = {'semver': semver}
        self.assertTrue(semver_check.is_match(stdin=stdin, args=args))

    def test_git_version_greater_than2(self):
        """Simple match with GE operator."""
        stdin = ("git version 2.10.2", "")
        semver = ">=1.11.3f"
        args = {'semver': semver}
        self.assertTrue(semver_check.is_match(stdin=stdin, args=args))

    def test_git_version_greater_than3(self):
        """Simple match with GE operator."""
        stdin = ("git version 2.10.2z", "")
        semver = ">=2.10.2a"
        args = {'semver': semver}
        self.assertTrue(semver_check.is_match(stdin=stdin, args=args))

    def test_git_version_equal_prefix(self):
        """Simple match with using prefix."""
        stdin = ("git version 2.10.2", "")
        semver = "2.10.2"
        prefix = 'git version '
        args = {'semver': semver, 'prefix': prefix}
        self.assertTrue(semver_check.is_match(stdin=stdin, args=args))

    def test_git_ver_equal_bad_prefix(self):
        """Simple mis-match via missing prefix."""
        stdin = ("TIG version 2.10.2", "")
        semver = "2.10.2"
        prefix = 'git version '
        args = {'semver': semver, 'prefix': prefix}
        self.assertFalse(semver_check.is_match(stdin=stdin, args=args))

    def test_curl_version_prefix(self):
        """Simple match using prefix."""
        stdin = (("curl 7.50.1 (x86_64-apple-darwin15.6.0) libcurl/7.50.1 "
                  "SecureTransport zlib/1.2.5"),
                 "")
        semver = ">=5.99.99"
        prefix = "curl "
        args = {'semver': semver, 'prefix': prefix}
        self.assertTrue(semver_check.is_match(stdin=stdin, args=args))

    def test_java_version_prefix(self):
        """Simple match using prefix."""
        stdin = ('java version "1.8.0_102"', "")
        semver = "1.8.0_102"
        prefix = 'java version "'
        args = {'semver': semver, 'prefix': prefix}
        self.assertTrue(semver_check.is_match(stdin=stdin, args=args))

    def test_java_ver_bad_prefix(self):
        """Simple mis-match via prefix."""
        stdin = ('TEA version "1.8.0_102"', "")
        semver = "1.8.0"
        prefix = 'java version "'
        args = {'semver': semver, 'prefix': prefix}
        self.assertFalse(semver_check.is_match(stdin=stdin, args=args))

    def test_java_version_ge(self):
        """Simple match using >= operator."""
        stdin = ('java version "1.8.0_102"', "")
        semver = ">=1.8.0_100"
        prefix = 'java version "'
        args = {'semver': semver, 'prefix': prefix}
        self.assertTrue(semver_check.is_match(stdin=stdin, args=args))

    def test_java_version_too_old(self):
        """Simple mis-match using >= operator."""
        stdin = ('java version "1.8.0_102"', "")
        semver = ">=1.8.0_103"
        prefix = 'java version "'
        args = {'semver': semver, 'prefix': prefix}
        self.assertFalse(semver_check.is_match(stdin=stdin, args=args))

    def test_java_version_too_old2(self):
        """Simple mis-match using >= operator."""
        stdin = ('java version "1.8.0_102"', "")
        semver = ">=1.8.0_1003"
        prefix = 'java version "'
        args = {'semver': semver, 'prefix': prefix}
        self.assertFalse(semver_check.is_match(stdin=stdin, args=args))

    def test_openssl_ver_prefix(self):
        """Simple match using prefix."""
        stdin = ("OpenSSL 1.0.2h  3 May 2016", "")
        semver = "1.0.2h"
        prefix = "OpenSSL "
        args = {'semver': semver, 'prefix': prefix}
        self.assertTrue(semver_check.is_match(stdin=stdin, args=args))

    def test_openssl_ver_too_old(self):
        """Simple mis-match via old version in alpha portion."""
        stdin = ("OpenSSL 1.0.2h  3 May 2016", "")
        semver = "1.0.2i"
        prefix = "OpenSSL "
        args = {'semver': semver, 'prefix': prefix}
        self.assertFalse(semver_check.is_match(stdin=stdin, args=args))

    def test_openssl_ver_too_old_gt(self):
        """Simple mis-match using too old version in alpha portion"""
        stdin = ("OpenSSL 1.0.2h  3 May 2016", "")
        semver = ">=1.0.2i"
        prefix = "OpenSSL "
        args = {'semver': semver, 'prefix': prefix}
        self.assertFalse(semver_check.is_match(stdin=stdin, args=args))

def _main():
    unittest.TestLoader().loadTestsFromTestCase(SemVerTest)

if __name__ == '__main__':
    _main()
