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
            transaction_id, request_domains = dns_packet

            print(transaction_id)

            if request_domains[0] == 'exit':
                break

            ip, cache_hit = self.resolver.resolve_dns(request_domains[0])

            # Construct DNS response packet and send it back to the client
            response_data = self.construct_dns_response(transaction_id, request_domains[0], ip)
            server_socket.sendto(response_data, client_address)

            print(f'Resolved: {request_domains[0]} => {ip} (Cache {"hit" if cache_hit else "miss"})')

        server_socket.close()

    def construct_dns_response(self, transaction_id, request_domain, ip):
        # Extract transaction ID from the DNS request packet
        response_transaction_id = transaction_id

        # Create the DNS response packet
        response_packet = response_transaction_id + b'\x81\x80' + b'\x00\x01' + b'\x00\x01' + b'\x00\x00' + b'\x00\x00'

        # Add the question section to the response packet
        response_packet += self.create_question_section(request_domain)

        # Add the answer section to the response packet
        response_packet += self.create_answer_section(request_domain, ip)

        return response_packet

    def create_question_section(self, request_domain):
        # Create the question section using the requested domain
        question_section = b''
        for part in request_domain.split('.'):
            length = len(part)
            question_section += bytes([length]) + part.encode()

        question_section += b'\x00'  # Terminating byte for the domain name
        question_section += b'\x00\x01'  # Type: A (IPv4 address)
        question_section += b'\x00\x01'  # Class: IN (Internet)

        return question_section

    def create_answer_section(self, request_domain, ip):
        if ip is None:
            # Return empty answer section when IP address is None
            return b''

        # Create the answer section using the requested domain and resolved IP address
        answer_section = b'\xc0\x0c'  # Pointer to domain name (compressed format)
        answer_section += b'\x00\x01'  # Type: A (IPv4 address)
        answer_section += b'\x00\x01'  # Class: IN (Internet)
        answer_section += b'\x00\x00\x00\x05'  # TTL (5 seconds)
        answer_section += b'\x00\x04'  # Data length: 4 bytes
        answer_section += self.ip_to_bytes(ip)  # IP address in bytes

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
