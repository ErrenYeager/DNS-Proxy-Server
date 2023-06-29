import datetime
import socket
import json

from dns_parser import DNSParser


class DNSResolver:
    def __init__(self):
        with open("config.json", "r") as f:
            config = json.load(f)
        self.cache_expiration_time = config["cache-expiration-time"]
        self.external_dns_servers = config["external-dns-servers"]
        self.cache = {}

    def resolve_dns(self, domain, query_type, data):
        if (domain, query_type) in self.cache:
            answers, flags, timestamp = self.cache[(domain, query_type)]
            if (datetime.datetime.now().timestamp() - timestamp) <= self.cache_expiration_time:  # Check cache expiration time
                return answers, flags, True  # Cache hit

        for dns_server in self.external_dns_servers:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.sendto(data, (dns_server, 53))

                    # Receive the DNS response
                    response, _ = sock.recvfrom(512)

                timestamp = datetime.datetime.now().timestamp()
                answers, flags = DNSParser.parse_dns_response(response)

                self.cache[(domain, query_type)] = (answers, flags, timestamp)

                return answers, flags, False  # Cache miss
            except Exception as e:
                return None, None, False  # DNS resolution error
