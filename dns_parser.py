class DNSParser:
    @staticmethod
    def parse_dns_packet(data):
        header = data[:12]  # DNS header is 12 bytes
        questions = data[12:]  # Questions section starts from the 13th byte onwards

        # Parse header
        transaction_id = header[:2]
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

        return transaction_id, question_parts
