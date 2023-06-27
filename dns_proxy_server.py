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

            answers, cache_hit = self.resolver.resolve_dns(domain, query_type, data)

            # Construct DNS response packet and send it back to the client
            response_data = self.construct_dns_response(transaction_id, flags, question_count, data[12:], query_type, query_class, answers)
            server_socket.sendto(response_data, client_address)

            print(f'Resolved: {domain} (Cache {"hit" if cache_hit else "miss"})')

        server_socket.close()

    def construct_dns_response(self, transaction_id, flags, question_count, queries, query_type, query_class, answers):

        # Create response header
        header = transaction_id + flags + question_count

        header += len(answers).to_bytes(2, "big")  # Answer Count

        header += b'\x00\x00' + b'\x00\x00'  # Authority flags (for other kind of records)

        # Create the DNS response packet
        response_packet = header

        # Add the question section to the response packet
        response_packet += queries

        # Add the answer section to the response packet
        response_packet += self.create_answer_section(query_type, query_class, answers)

        return response_packet

    def create_answer_section(self, query_type, query_class, answers):
        answer_section = b'\xc0\x0c'

        # Create answer records for each IP address
        for answer_type, answer_class, ttl, data_length, ip_address in answers:
            # Create record type and class fields
            record_type = answer_type.to_bytes(2, "big")
            record_class = answer_class.to_bytes(2, "big")

            # Create TTL field
            ttl_bytes = ttl.to_bytes(4, byteorder='big')

            # Create RDLength field
            rd_length = len(ip_address.split('.'))  # Assuming IPv4 addresses
            rd_length = rd_length.to_bytes(2, byteorder='big')

            # Create RData field
            rdata = b''
            for octet in ip_address.split('.'):
                rdata += int(octet).to_bytes(1, byteorder='big')

            # Construct the answer record
            answer_record = record_type + record_class + ttl_bytes + rd_length + rdata

            # Append the answer record to the answer section
            answer_section += answer_record

        return answer_section


if __name__ == '__main__':
    dns_proxy = DNSProxyServer()
    dns_proxy.start_dns_proxy()
