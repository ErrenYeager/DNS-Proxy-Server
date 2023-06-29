import socket
import json
import redis

from dns_parser import DNSParser


class DNSResolver:
    def __init__(self):
        with open("config.json", "r") as f:
            config = json.load(f)
        self.cache_expiration_time = config["cache-expiration-time"]
        self.external_dns_servers = config["external-dns-servers"]
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)  # Connect to Redis server

    def resolve_dns(self, domain, query_type, data):
        cache_key = f"{domain}:{query_type}"
        cache_data = self.redis_client.get(cache_key)

        if cache_data:
            answers, flags = json.loads(cache_data)
            return answers, flags, True  # Cache hit

        for dns_server in self.external_dns_servers:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.sendto(data, (dns_server, 53))

                    # Receive the DNS response
                    response, _ = sock.recvfrom(512)

                answers, flags = DNSParser.parse_dns_response(response)

                # Store the response in Redis cache
                cache_value = json.dumps((answers, flags))
                self.redis_client.setex(cache_key, self.cache_expiration_time, cache_value)

                return answers, flags, False  # Cache miss
            except Exception as e:
                return 0, None, False  # DNS resolution error
