import struct
import socket


class DNSParser:
    @staticmethod
    def parse_dns_packet(data):
        header = data[:12]  # DNS header is 12 bytes
        questions = data[12:]  # Questions section starts from the 13th byte onwards

        # Parse header
        transaction_id = header[:2]
        flags = header[2:4]
        question_count = header[4:6]
        # Extract other header fields as needed (e.g., flags, counts, etc.)

        # Parse questions section
        question_parts = []
        idx = 0
        while idx < len(questions):
            length = questions[idx]
            if length == 0:
                break
            question_parts.append(questions[idx + 1:idx + length + 1].decode())
            idx += length + 1

        query_type = struct.unpack("!H", questions[-4:-2])[0]

        if query_type == 28:
            query_type = 'AAAA'
        elif query_type == 1:
            query_type = 'A'
        else:
            raise ValueError("Unsupported query type")

        query_class = questions[-2:]

        return transaction_id, question_count, question_parts, query_type, query_class

    @staticmethod
    def parse_dns_response(response):
        # Parse the header
        header = struct.unpack('!6H', response[:12])
        flags = header[1]
        question_count = header[2]
        answer_count = header[3]
        authority_count = header[4]
        additional_count = header[5]

        # Parse the question section
        offset = 12
        for _ in range(question_count):
            while response[offset] != 0:
                offset += 1
            offset += 5

        # Parse the answer section
        addresses = []

        for _ in range(answer_count):
            name, offset = DNSParser.read_name(response, offset)

            answer_type, answer_class, ttl, data_length = struct.unpack('!HHIH', response[offset:offset+10])
            offset += 10

            if answer_type == 1:  # A record
                ip_address_bytes = response[offset:offset+4]
                ip_address = socket.inet_ntop(socket.AF_INET, ip_address_bytes)
                addresses.append((answer_type, answer_class, ttl, data_length, ip_address))

            elif answer_type == 28:  # AAAA record
                ip_address_bytes = response[offset:offset+16]
                ip_address = socket.inet_ntop(socket.AF_INET6, ip_address_bytes)
                addresses.append((answer_type, answer_class, ttl, data_length, ip_address))

            offset += data_length

        return addresses, flags

    @staticmethod
    def read_name(response, offset):
        name_parts = []
        while True:
            length = response[offset]
            if length == 0:
                break
            elif length >= 192:  # Compression
                pointer = struct.unpack('!H', response[offset:offset+2])[0] & 0x3FFF
                name, _ = DNSParser.read_name(response, pointer)
                name_parts.append(name)
                offset += 2
                break
            else:
                offset += 1
                name_part = response[offset:offset+length].decode('utf-8')
                name_parts.append(name_part)
                offset += length

        return '.'.join(name_parts), offset