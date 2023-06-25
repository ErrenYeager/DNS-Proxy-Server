import socket
from dns_parser import DNSParser
from dns_resolver import DNSResolver


class DNSProxyServer:
    def __init__(self):
        self.parser = DNSParser()
        self.resolver = DNSResolver()

    def start_dns_proxy(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('localhost', 53))  # Bind to the DNS port (53)

        print('DNS proxy server started. Listening on port 53...')

        while True:
            data, client_address = server_socket.recvfrom(1024)

            dns_packet = self.parser.parse_dns_packet(data)
            request_domain = self.parser.extract_domain_name(dns_packet)

            if request_domain == 'exit':
                break

            ip, cache_hit = self.resolver.resolve_dns(request_domain)

            # Construct DNS response packet and send it back to the client
            response_data = self.construct_dns_response(dns_packet, ip)
            server_socket.sendto(response_data, client_address)

            print(f'Resolved: {request_domain} => {ip} (Cache {"hit" if cache_hit else "miss"})')

        server_socket.close()

    def construct_dns_response(self, dns_packet, ip):
        # TODO:Implement DNS response construction logic here
        pass


if __name__ == '__main__':
    dns_proxy = DNSProxyServer()
    dns_proxy.start_dns_proxy()
