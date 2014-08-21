# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import unittest
import logging

import pep8
from errbot.backends.test import FullStackTest, pushMessage, popMessage

import dnsnative

# Make the test less noisy.
logging.getLogger('yapsy').setLevel(logging.CRITICAL)
logging.getLogger('Rocket.Errors').setLevel(logging.CRITICAL)
logging.getLogger('errbot.plugins.DNSNative').setLevel(logging.CRITICAL)


class DNSNativeIsIPTest(unittest.TestCase):
    """Test our is_ip() method."""

    def test_is_ip_v4(self):
        """Test if we can determine the passed value is an IPv4 address.
        IP address."""
        result = dnsnative.DNSNative.is_ip('10.120.1.1')
        self.assertEqual(result, True)

    def test_is_ip_ipv6(self):
        """Test if we can determine the passed value is an IPv6 address.
        IP address."""
        result = dnsnative.DNSNative.is_ip('::1')
        self.assertEqual(result, True)

    def test_is_ip_ipv6(self):
        """Test if we can determine the passed value isn't an IP address."""
        result = dnsnative.DNSNative.is_ip('abra.cada.bra')
        self.assertEqual(result, False)


class DNSNativeGetHostByTest(unittest.TestCase):
    """Test our get_host_by_* methods."""

    def test_get_host_by_ip_v4_localhost(self):
        """Resolve the 127.0.0.1 to localhost."""
        expected = "127.0.0.1 resolves to localhost"
        result = dnsnative.DNSNative.get_host_by_ip('127.0.0.1')
        self.assertRegex(result, expected)

    def test_get_host_by_ip_v4_unknown(self):
        """Try to resolve something that's unlikely to have a PTR."""
        expected = "Could not resolve 255.255.255.254."
        result = dnsnative.DNSNative.get_host_by_ip('255.255.255.254')
        self.assertEqual(result, expected)

    def test_get_host_by_ip_v4_google_dns(self):
        """Resolve a known public IPv4 address."""
        expected = "8.8.4.4 resolves to google-public-dns-b.google.com."
        result = dnsnative.DNSNative.get_host_by_ip('8.8.4.4')
        self.assertEqual(result, expected)

    def test_get_host_by_ip_v6_localhost(self):
        """Resolve ::1 to localhsot."""
        expected = "::1 resolves to localhost."
        result = dnsnative.DNSNative.get_host_by_ip('::1')
        self.assertEqual(result, expected)

    def test_get_host_by_ip_v6_google_dns(self):
        """Resolve a know public IPv6 address."""
        expected = ('2001:4860:4860::8844 resolves to google-public-dns-'
                    'b.google.com.')
        result = dnsnative.DNSNative.get_host_by_ip('2001:4860:4860::8844')
        self.assertEqual(result, expected)

    def test_get_host_by_name_localhost(self):
        """Resolve localhost to it's IPv4 and IPv6 counterparts."""
        # Test that localhost resolves to IPv4 and IPv6.
        expected = "localhost resolves to:\n • ::1\n • 127.0.0.1"
        result = dnsnative.DNSNative.get_host_by_name('localhost')
        self.assertRegex(result, expected)

    def test_get_host_by_name_single_answer(self):
        """Resolve an address that only gives a single reply."""
        expected = 'tweakers.net resolves to 213.239.154.20.'
        result = dnsnative.DNSNative.get_host_by_name('tweakers.net')
        self.assertEqual(result, expected)

    def test_get_host_by_name_google_dns(self):
        """Resolve a Google Public DNS hostname to its IPv4 and IPv6
        counterparts."""
        result = dnsnative.DNSNative.get_host_by_name('google-public-dns-'
                                                      'b.google.com')
        self.assertRegex(result,
                         'google-public-dns-b.google.com resolves to')
        self.assertRegex(result, '8.8.4.4')
        self.assertRegex(result, '2001:4860:4860::8844')

    def test_get_host_by_name_unknown(self):
        """Try to resolve a bogus hostname."""
        expected = 'Could not resolve abra.cada.bra.'
        result = dnsnative.DNSNative.get_host_by_name('abra.cada.bra')
        self.assertEqual(result, expected)


class DNSNativeBotTests(FullStackTest):
    """Test interaction with the bot. In this case we need a complete bot, send
    messages to the bot and check the reply."""

    def setUp(self):
        me = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
        # Adding /la/bla to path is needed because of the path mangling
        # FullStackTest does on extra_test_file.
        plugin_dir = os.path.join(me, 'la', 'bla')
        # Call our parent's setUp() method but pass our directory to
        # extra_test_file so our plugin is loaded.
        super(DNSNativeBotTests, self).setUp(extra_test_file=plugin_dir)

    def test_host(self):
        """Send host command to the bot, verify we get help back."""
        pushMessage('!host')
        self.assertIn('host: provide a hostname or an IP', popMessage())

    def test_host_help(self):
        """Send host help command, verify we get help back."""
        pushMessage('!host help')
        self.assertIn('host: provide a hostname or an IP', popMessage())

    def test_host_hostname(self):
        """Send host hostname, verify we get the correctly reply."""
        pushMessage('!host google-public-dns-b.google.com')
        response = popMessage()
        self.assertRegex(response,
                         'google-public-dns-b.google.com resolves to')
        self.assertRegex(response, '8.8.4.4')
        self.assertRegex(response, '2001:4860:4860::8844')

    def test_host_hostnames(self):
        """Send host with multiple hostnames, verify we get multiple responses
        back with the correct content."""
        pushMessage('!host google-public-dns-b.google.com google-public-dns'
                    '-b.google.com')
        response1 = popMessage()
        response2 = popMessage()
        self.assertRegex(response1,
                         'google-public-dns-b.google.com resolves to')
        self.assertRegex(response2,
                         'google-public-dns-b.google.com resolves to')
        self.assertRegex(response1, '8.8.4.4')
        self.assertRegex(response1, '2001:4860:4860::8844')
        self.assertRegex(response2, '8.8.4.4')
        self.assertRegex(response2, '2001:4860:4860::8844')

    def test_host_ip(self):
        """Send host IP, verify we get the expected hostname back."""
        # IPv4
        pushMessage('!host 8.8.4.4')
        self.assertEqual('8.8.4.4 resolves to google-public-dns-b.google.com.',
                         popMessage())
        # IPv6
        pushMessage('!host 2001:4860:4860::8844')
        self.assertEqual(
            '2001:4860:4860::8844 resolves to '
            'google-public-dns-b.google.com.', popMessage())

    def test_host_ips(self):
        """Send host with multiple IP's, verify we get the expected hostnames
        back."""
        pushMessage('!host 8.8.4.4 2001:4860:4860::8844')
        self.assertEqual('8.8.4.4 resolves to google-public-dns-b.google.com.',
                         popMessage())
        self.assertEqual(
            '2001:4860:4860::8844 resolves to '
            'google-public-dns-b.google.com.', popMessage())


class TestCodeFormat(unittest.TestCase):
    """Test suite that validates our code adheres to certain standards."""

    def test_pep8_conformance(self):
        """Test that we conform to PEP8."""
        pep8style = pep8.StyleGuide(quiet=True)
        result = pep8style.check_files(['dnsnative.py', 'test_dnsnative.py'])
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")


if __name__ == '__main__':
        unittest.main()
