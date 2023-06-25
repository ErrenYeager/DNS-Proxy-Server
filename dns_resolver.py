import datetime
import socket


class DNSResolver:
    def __init__(self):
        self.cache = {}

    def resolve_dns(self, domain):
        if domain in self.cache:
            ip, timestamp = self.cache[domain]
            if (timestamp - datetime.datetime.now().timestamp()) <= 5:  # Check cache expiration time
                return ip, True  # Cache hit

        try:
            ip = socket.gethostbyname(domain)
            timestamp = datetime.datetime.now().timestamp()
            self.cache[domain] = (ip, timestamp)
            return ip, False  # Cache miss
        except Exception as e:
            return None, False  # DNS resolution error
