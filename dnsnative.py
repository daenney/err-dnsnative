from __future__ import unicode_literals
import socket
import logging

from errbot import BotPlugin, botcmd

log = logging.getLogger(name='errbot.plugins.DNSNative')


class DNSNative(BotPlugin):

    min_err_version = '2.0.0-rc1'

    if hasattr(socket, 'setdefaulttimeout'):
        socket.setdefaulttimeout(5)

    @botcmd(split_args_with=None)
    def host(self, message, args):
        """Resolve a hostname to IP('s) or an IP to its hostname."""
        if not args:
            yield self.host_help()
        for arg in args:
            if self.is_ip(arg):
                yield self.get_host_by_ip(arg)
            else:
                yield self.get_host_by_name(arg)

    @botcmd
    def host_help(self, *args):
        """Give the user some help."""
        return ("host: provide a hostname or an IP and I'll look it up for "
                "you. You can also provide multiple hostnames or IP's as "
                "long as they are separated by spaces.")

    @staticmethod
    def is_ip(value):
        """Check if the value passed is an IPv4 or IPv6 address."""
        log.debug("Received a value of {0}".format(value))
        is_ip = False
        try:
            socket.inet_pton(socket.AF_INET, value)
            is_ip = True
            log.debug("{0} found to be an IPv4 address.".format(value))
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, value)
                is_ip = True
                log.debug("{0} found to be an IPv6 address.".format(value))
            except socket.error:
                log.debug("{0} is not an IP.".format(value))

        return is_ip

    @staticmethod
    def get_host_by_ip(ip):
        """Do a reverse lookup and find the IP's corresponding hostname(s)."""
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return "{0} resolves to {1}.".format(
                ip, hostname)
        except socket.herror:
            return "Could not resolve {0}.".format(ip)

    @staticmethod
    def get_host_by_name(name):
        """Do a lookup and find the hostname's corresponding IP(s)."""
        try:
            # We're using .getaddrinfo since gethostbyname_ex only deals with
            # IPv4. It's slightly unfortunate since this doesn't give us the
            # CNAMES but at least we can deal with legacy IP protocol v4 and
            # the current v6 standard.
            result = socket.getaddrinfo(name, 80, 0, 0, socket.SOL_TCP)
            log.debug("Got {0} for {1}".format(result, name))
            ips = []
            for item in result:
                ips.append(item[4][0])
            return "{0} resolves to {1}.".format(name, ', '.join(ips))
        except socket.gaierror:
            return "Could not resolve {0}.".format(name)
