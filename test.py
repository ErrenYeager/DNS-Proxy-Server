import unittest
from dns_proxy_server import DNSProxyServer
from dns_resolver import DNSResolver


class DNSProxyServerTests(unittest.TestCase):
    def setUp(self):
        self.resolver = DNSResolver()

    # Test case 1: A record response
    def test_construct_dns_response(self):
        dns_proxy = DNSProxyServer()

        transaction_id = b'\x12\x34'
        flags = 0x8180
        question_count = b'\x00\x01'
        queries = b'\x03www\x06google\x03com\x00'
        answers = [
            (1, 1, 3600, 4, '192.0.2.1')
        ]

        expected_response = b'\x124\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x03www\x06google\x03com\x00\xc0\x0c\x00\x01\x00\x01\x00\x00\x0e\x10\x00\x04\xc0\x00\x02\x01'

        response_packet = dns_proxy.construct_dns_response(transaction_id, flags, question_count, queries, answers)
        self.assertEqual(response_packet, expected_response)

        # Test case 2: AAAA record response
        answers = [
            (28, 1, 3600, 16, '2001:db8::1')
        ]

        expected_response = b'\x124\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x03www\x06google\x03com\x00\xc0\x0c\x00\x1c\x00\x01\x00\x00\x0e\x10\x00\x10 \x01\r\xb8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'

        response_packet = dns_proxy.construct_dns_response(transaction_id, flags, question_count, queries, answers)
        self.assertEqual(response_packet, expected_response)

    # Test case 2: cache hit
    def test_cache_hit(self):
        domain = "example.com"
        query_type = "A"
        data = b'\xdb\x84\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01'

        # Resolve the DNS query once
        answers, flags, cache_flag = self.resolver.resolve_dns(domain, query_type, data)
        self.assertIsNotNone(answers)
        self.assertIsNotNone(flags)
        self.assertFalse(flags & 0x0F)  # Check that the response code is not an error

        # Resolve the same DNS query again
        cached_answers, cached_flags, cache_flag = self.resolver.resolve_dns(domain, query_type, data)
        self.assertEqual([tuple(i) for i in answers], [tuple(i) for i in cached_answers])  # Cached answers should match the original response
        self.assertEqual(flags, cached_flags)  # Cached flags should match the original response
        self.assertTrue(cache_flag)

    def test_cache_miss(self):
        domain = "example2.com"
        query_type = "A"
        data = b'\xdb\x84\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01'

        # Resolve the DNS query
        answers, flags, cache_flag = self.resolver.resolve_dns(domain, query_type, data)
        self.assertIsNotNone(answers)
        self.assertIsNotNone(flags)
        self.assertFalse(flags & 0x0F)  # Check that the response code is not an error

        # Modify the DNS query type to trigger a cache miss
        modified_query_type = "AAAA"
        modified_data = b'\xac\x92\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x1c\x00\x01'

        # Resolve the modified DNS query
        cached_answers, cached_flags, cache_flag = self.resolver.resolve_dns(domain, modified_query_type, modified_data)
        self.assertIsNotNone(cached_answers)
        self.assertIsNotNone(cached_flags)
        self.assertFalse(cached_flags & 0x0F)  # Check that the response code is not an error
        self.assertNotEqual(answers, cached_answers)  # Cached answers should be different from the original response
        self.assertFalse(cache_flag)


if __name__ == '__main__':
    unittest.main()
