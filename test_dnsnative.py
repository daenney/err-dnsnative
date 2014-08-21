# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from errbot.backends.test import testbot, push_message, pop_message

import dnsnative

# Make the test less noisy.
logging.getLogger('yapsy').setLevel(logging.CRITICAL)
logging.getLogger('Rocket.Errors').setLevel(logging.CRITICAL)
logging.getLogger('errbot.plugins.DNSNative').setLevel(logging.CRITICAL)


class TestIsIP(object):
    """Test our is_ip() method."""

    def test_is_ip_v4(self):
        """Test if we can determine the passed value is an IPv4 address.
        IP address."""
        assert dnsnative.DNSNative.is_ip('10.120.1.1') is True

    def test_is_ip_ipv6(self):
        """Test if we can determine the passed value is an IPv6 address.
        IP address."""
        assert dnsnative.DNSNative.is_ip('::1') is True

    def test_is_not_ip(self):
        """Test if we can determine the passed value isn't an IP address."""
        assert dnsnative.DNSNative.is_ip('abra.cada.bra') is False


class TestGetHostBy(object):
    """Test our get_host_by_* methods."""

    def test_get_host_by_ip_v4_localhost(self):
        """Resolve the 127.0.0.1 to localhost."""
        expected = "127.0.0.1 resolves to localhost"
        result = dnsnative.DNSNative.get_host_by_ip('127.0.0.1')
        assert expected in result

    def test_get_host_by_ip_v4_unknown(self):
        """Try to resolve something that's unlikely to have a PTR."""
        expected = "Could not resolve 255.255.255.254."
        result = dnsnative.DNSNative.get_host_by_ip('255.255.255.254')
        assert result == expected

    def test_get_host_by_ip_v4_google_dns(self):
        """Resolve a known public IPv4 address."""
        expected = "8.8.4.4 resolves to google-public-dns-b.google.com."
        result = dnsnative.DNSNative.get_host_by_ip('8.8.4.4')
        assert result == expected

    def test_get_host_by_ip_v6_localhost(self):
        """Resolve ::1 to localhsot."""
        expected = "::1 resolves to localhost"
        result = dnsnative.DNSNative.get_host_by_ip('::1')
        assert expected in result

    def test_get_host_by_ip_v6_google_dns(self):
        """Resolve a know public IPv6 address."""
        expected = ('2001:4860:4860::8844 resolves to google-public-dns-'
                    'b.google.com.')
        result = dnsnative.DNSNative.get_host_by_ip('2001:4860:4860::8844')
        assert result == expected

    def test_get_host_by_name_localhost(self):
        """Resolve localhost to it's IPv4 and IPv6 counterparts."""
        # Test that localhost resolves to IPv4 and IPv6.
        expected = "localhost resolves to:\n • ::1\n • 127.0.0.1"
        result = dnsnative.DNSNative.get_host_by_name('localhost')
        assert expected in result

    def test_get_host_by_name_single_answer(self):
        """Resolve an address that only gives a single reply."""
        expected = 'tweakers.net resolves to 213.239.154.20.'
        result = dnsnative.DNSNative.get_host_by_name('tweakers.net')
        assert result == expected

    def test_get_host_by_name_google_dns(self):
        """Resolve a Google Public DNS hostname to its IPv4 and IPv6
        counterparts."""
        result = dnsnative.DNSNative.get_host_by_name('google-public-dns-'
                                                      'b.google.com')
        assert 'google-public-dns-b.google.com resolves to' in result
        assert '8.8.4.4' in result
        assert '2001:4860:4860::8844' in result

    def test_get_host_by_name_unknown(self):
        """Try to resolve a bogus hostname."""
        expected = 'Could not resolve abra.cada.bra.'
        result = dnsnative.DNSNative.get_host_by_name('abra.cada.bra')
        assert result == expected


class TestBotInteractions(object):
    """Test interaction with the bot. In this case we need a complete bot, send
    messages to the bot and check the reply."""

    extra_plugin_dir = '.'

    def test_host(self, testbot):
        """Send host command to the bot, verify we get help back."""
        push_message('!host')
        assert 'host: provide a hostname or an IP' in pop_message()

    def test_host_help(self, testbot):
        """Send host help command, verify we get help back."""
        push_message('!host help')
        assert 'host: provide a hostname or an IP' in pop_message()

    def test_host_hostname(self, testbot):
        """Send host hostname, verify we get the correctly reply."""
        push_message('!host google-public-dns-b.google.com')
        response = pop_message()
        assert 'google-public-dns-b.google.com resolves to' in response
        assert '8.8.4.4' in response
        assert '2001:4860:4860::8844' in response

    def test_host_hostnames(self, testbot):
        """Send host with multiple hostnames, verify we get multiple responses
        back with the correct content."""
        push_message('!host google-public-dns-b.google.com google-public-dns'
                     '-b.google.com')
        response1 = pop_message()
        response2 = pop_message()
        assert 'google-public-dns-b.google.com resolves to' in response1
        assert 'google-public-dns-b.google.com resolves to' in response2
        assert '8.8.4.4' in response1
        assert '8.8.4.4' in response2
        assert '2001:4860:4860::8844' in response1
        assert '2001:4860:4860::8844' in response2

    def test_host_ip(self, testbot):
        """Send host IP, verify we get the expected hostname back."""
        # IPv4
        push_message('!host 8.8.4.4')
        resp = pop_message()
        assert '8.8.4.4 resolves to google-public-dns-b.google.com.' in resp
        # IPv6
        push_message('!host 2001:4860:4860::8844')
        resp = pop_message()
        assert ('2001:4860:4860::8844 resolves to '
                'google-public-dns-b.google.com.') in resp

    def test_host_ips(self, testbot):
        """Send host with multiple IP's, verify we get the expected hostnames
        back."""
        push_message('!host 8.8.4.4 2001:4860:4860::8844')
        resp = pop_message()
        assert '8.8.4.4 resolves to google-public-dns-b.google.com.' in resp

        assert ('2001:4860:4860::8844 resolves to '
                'google-public-dns-b.google.com.') in pop_message()
