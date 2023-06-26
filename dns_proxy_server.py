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

            transaction_id, flags, question_count, request_domains, query_type, query_class = self.parser.parse_dns_packet(data)

            domain = ".".join(request_domains)

            if domain == 'exit.com':
                break

            ip, cache_hit = self.resolver.resolve_dns(domain, data)

            # Construct DNS response packet and send it back to the client
            response_data = self.construct_dns_response(transaction_id, flags, question_count, data[12:], query_type, query_class, ip)
            server_socket.sendto(response_data, client_address)

            print(f'Resolved: {domain} => {ip} (Cache {"hit" if cache_hit else "miss"})')

        server_socket.close()

    def construct_dns_response(self, transaction_id, flags, question_count, queries, query_type, query_class, ip):

        # Create response header
        header = transaction_id + flags + question_count + b'\x00\x01' + b'\x00\x00' + b'\x00\x00'

        # Create the DNS response packet
        response_packet = header

        # Add the question section to the response packet
        response_packet += queries

        # Add the answer section to the response packet
        response_packet += self.create_answer_section(query_type, query_class, ip)

        return response_packet

    def create_answer_section(self, query_type, query_class, answer):
        if answer is None:
            # Return empty answer section when IP address is None
            return b''

        # Create the answer section using the requested domain and resolved IP address
        # TODO: FIX ALL THIS
        answer_section = b'\xc0\x0c'  # Pointer to domain name (compressed format)
        answer_section += b'\x00\x01' if query_type == "A" else b'\x00\x1c'  # Type
        answer_section += query_class  # Class
        answer_section += b'\x00\x00\x00\x05'  # TTL (5 seconds)
        answer_section += b'\x00\x04'  # Data length: 4 bytes
        answer_section += self.ip_to_bytes(answer)  # IP address in bytes

        return answer_section


    @staticmethod
    def ip_to_bytes(ip):
        # Convert the IP address from string to bytes
        ip_bytes = b''
        for part in ip.split('.'):
            ip_bytes += bytes([int(part)])
        return ip_bytes


if __name__ == '__main__':
    dns_proxy = DNSProxyServer()
    dns_proxy.start_dns_proxy()
