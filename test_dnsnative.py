import unittest
import os

import pep8
from errbot.backends.test import FullStackTest, pushMessage, popMessage

import dnsnative


class DNSNativeUtilitiesTest(unittest.TestCase):
    def test_is_ip(self):
        result = dnsnative.DNSNative.is_ip('10.120.1.1')
        self.assertEqual(result, True)

        result = dnsnative.DNSNative.is_ip('::1')
        self.assertEqual(result, True)

        result = dnsnative.DNSNative.is_ip('abra.cada.bra')
        self.assertEqual(result, False)

    def test_get_host_by_ip(self):
        expected = "127.0.0.1 resolves to localhost."
        result = dnsnative.DNSNative.get_host_by_ip('127.0.0.1')
        self.assertEqual(result, expected)

        expected = "Could not resolve 255.255.255.254."
        result = dnsnative.DNSNative.get_host_by_ip('255.255.255.254')
        self.assertEqual(result, expected)

        expected = "8.8.4.4 resolves to google-public-dns-b.google.com."
        result = dnsnative.DNSNative.get_host_by_ip('8.8.4.4')
        self.assertEqual(result, expected)

        expected = "::1 resolves to localhost."
        result = dnsnative.DNSNative.get_host_by_ip('::1')
        self.assertEqual(result, expected)

        expected = ('2001:4860:4860::8844 resolves to google-public-dns-'
                    'b.google.com.')
        result = dnsnative.DNSNative.get_host_by_ip('2001:4860:4860::8844')
        self.assertEqual(result, expected)

    def test_get_host_by_name(self):
        expected = "localhost resolves to ::1, 127.0.0.1"
        result = dnsnative.DNSNative.get_host_by_name('localhost')
        self.assertRegex(result, expected)

        expected = ('google-public-dns-b.google.com resolves to 8.8.4.4,'
                    ' 2001:4860:4860::8844.')
        result = dnsnative.DNSNative.get_host_by_name('google-public-dns-'
                                                      'b.google.com')
        self.assertEqual(result, expected)

        expected = 'Could not resolve abra.cada.bra.'
        result = dnsnative.DNSNative.get_host_by_name('abra.cada.bra')
        self.assertEqual(result, expected)


class DNSNativeBotTests(FullStackTest):
    def setUp(self):
        me = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
        # Adding /la/bla to path is needed because of the path mangling
        # FullStackTest does on extra_test_file
        plugin_dir = os.path.join(me, 'la', 'bla')
        super(DNSNativeBotTests, self).setUp(extra_test_file=plugin_dir)

    def test_host(self):
        pushMessage('!host')
        self.assertIn('host: provide a hostname or an IP', popMessage())

    def test_host_help(self):
        pushMessage('!host help')
        self.assertIn('host: provide a hostname or an IP', popMessage())

    def test_host_hostname(self):
        pushMessage('!host google-public-dns-b.google.com')
        self.assertEqual('google-public-dns-b.google.com resolves to 8.8.4.4,'
                         ' 2001:4860:4860::8844.', popMessage())

    def test_host_hostnames(self):
        pushMessage('!host google-public-dns-b.google.com google-public-dns'
                    '-b.google.com')
        self.assertEqual('google-public-dns-b.google.com resolves to 8.8.4.4,'
                         ' 2001:4860:4860::8844.', popMessage())
        self.assertEqual('google-public-dns-b.google.com resolves to 8.8.4.4,'
                         ' 2001:4860:4860::8844.', popMessage())

    def test_host_ip(self):
        pushMessage('!host 8.8.4.4')
        self.assertEqual('8.8.4.4 resolves to google-public-dns-b.google.com.',
                         popMessage())
        pushMessage('!host 2001:4860:4860::8844')
        self.assertEqual(
            '2001:4860:4860::8844 resolves to '
            'google-public-dns-b.google.com.', popMessage())

    def test_host_ips(self):
        pushMessage('!host 8.8.4.4 2001:4860:4860::8844')
        self.assertEqual('8.8.4.4 resolves to google-public-dns-b.google.com.',
                         popMessage())
        self.assertEqual(
            '2001:4860:4860::8844 resolves to '
            'google-public-dns-b.google.com.', popMessage())


class TestCodeFormat(unittest.TestCase):

    def test_pep8_conformance(self):
        """Test that we conform to PEP8."""
        pep8style = pep8.StyleGuide(quiet=True)
        result = pep8style.check_files(['dnsnative.py', 'test_dnsnative.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")
if __name__ == '__main__':
        unittest.main()
