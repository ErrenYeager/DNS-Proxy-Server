import socket
import unittest
from unittest.mock import patch
from dns_proxy_server import DNSProxyServer


class DNSProxyServerTests(unittest.TestCase):
    @patch('socket.socket')
    def test_construct_dns_response(self, mock_socket):
        dns_proxy = DNSProxyServer()

        # Test case 1: A record response
        transaction_id = b'\x12\x34'
        flags = 0x8180
        question_count = b'\x00\x01'
        queries = b'\x03www\x06google\x03com\x00'
        answers = [
            (b'\xc0\x0c', 1, 1, 3600, 4, '192.0.2.1')
        ]

        expected_response = b'\x124\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x03www\x06google\x03com\x00\xc0\x0c\x00\x01\x00\x01\x00\x00\x0e\x10\x00\x04\xc0\x00\x02\x01'

        response_packet = dns_proxy.construct_dns_response(transaction_id, flags, question_count, queries, answers)
        self.assertEqual(response_packet, expected_response)

        # Test case 2: AAAA record response
        answers = [
            (b'\xc0\x0c', 28, 1, 3600, 16, '2001:db8::1')
        ]

        expected_response = b'\x124\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x03www\x06google\x03com\x00\xc0\x0c\x00\x1c\x00\x01\x00\x00\x0e\x10\x00\x10 \x01\r\xb8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'

        response_packet = dns_proxy.construct_dns_response(transaction_id, flags, question_count, queries, answers)
        self.assertEqual(response_packet, expected_response)

    # @patch('socket.socket')
    # def test_start_dns_proxy(self, mock_socket):
    #     # Mock the socket object and its methods
    #     mock_socket_instance = mock_socket.return_value
    #     mock_socket_instance.recvfrom.return_value = (b'\x98\x81\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x06google\x03com\x00\x00\x01\x00\x01', ('client', 1234))
    #     mock_socket_instance.sendto.return_value = None
    #
    #     # Create an instance of DNSProxyServer
    #     dns_proxy = DNSProxyServer()
    #
    #     # Test starting DNS proxy
    #     with patch.object(dns_proxy, 'construct_dns_response') as mock_construct_dns_response:
    #         mock_construct_dns_response.return_value = b'response_packet'
    #
    #         with patch.object(dns_proxy.resolver, 'resolve_dns') as mock_resolve_dns:
    #             mock_resolve_dns.return_value = ([(b'\xc0\x0c', 1, 1, 3600, 4, '192.0.2.1')], 0x8180, False)
    #
    #             dns_proxy.start_dns_proxy()
    #
    #     # Assert calls to socket methods
    #     mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
    #     mock_socket_instance.bind.assert_called_once_with(('localhost', 53))
    #     mock_socket_instance.recvfrom.assert_called_once_with(1024)
    #     mock_socket_instance.sendto.assert_called_once_with(b'response_packet', ('client', 1234))

    # @patch('socket.socket')
    # def test_resolve_dns_cache_hit(self, mock_socket):
    #     dns_resolver = DNSProxyServer().resolver
    #     dns_resolver.cache = {
    #         ('example.com', 'A'): ([(b'\xc0\x0c', 1, 1, 3600, 4, '192.0.2.1')], 0x8180, 1234567890)
    #     }
    #
    #     # Test cache hit
    #     answers, flags, cache_hit = dns_resolver.resolve_dns('example.com', 'A', b'data')
    #     self.assertEqual(answers, [(b'\xc0\x0c', 1, 1, 3600, 4, '192.0.2.1')])
    #     self.assertEqual(flags, 0x8180)
    #     self.assertTrue(cache_hit)

    @patch('socket.socket')
    def test_resolve_dns_cache_miss(self, mock_socket):
        dns_resolver = DNSProxyServer().resolver

        # Mock the socket object and its methods
        mock_socket_instance = mock_socket.return_value
        mock_socket_instance.sendto.return_value = None
        mock_socket_instance.recvfrom.return_value = (b'response', ('dns_server', 53))

        # Test cache miss
        with patch.object(dns_resolver, 'parse_dns_response') as mock_parse_dns_response:
            mock_parse_dns_response.return_value = ([(b'\xc0\x0c', 1, 1, 3600, 4, '192.0.2.1')], 0x8180)

            answers, flags, cache_hit = dns_resolver.resolve_dns('example.com', 'A', b'data')

            # Assert calls to socket methods
            mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
            mock_socket_instance.sendto.assert_called_once_with(b'data', ('dns_server', 53))
            mock_socket_instance.recvfrom.assert_called_once_with(512)

            # Assert cache update
            self.assertEqual(answers, [(b'\xc0\x0c', 1, 1, 3600, 4, '192.0.2.1')])
            self.assertEqual(flags, 0x8180)
            self.assertFalse(cache_hit)

    # @patch('socket.socket')
    # def test_resolve_dns_resolution_error(self, mock_socket):
    #     dns_resolver = DNSProxyServer().resolver
    #
    #     # Mock the socket object and its methods
    #     mock_socket_instance = mock_socket.return_value
    #     mock_socket_instance.sendto.side_effect = Exception('Socket error')
    #
    #     # Test DNS resolution error
    #     answers, flags, cache_hit = dns_resolver.resolve_dns('example.com', 'A', b'data')
    #
    #     # Assert cache update
    #     self.assertIsNone(answers)
    #     self.assertIsNone(flags)
    #     self.assertFalse(cache_hit)


if __name__ == '__main__':
    unittest.main()
