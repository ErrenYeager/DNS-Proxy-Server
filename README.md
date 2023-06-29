# DNS Proxy Server

The DNS Proxy Server is a Python program that acts as a DNS proxy, receiving DNS queries from clients, resolving them using external DNS servers, and returning the responses back to the clients. It provides a caching mechanism to improve performance and reduce external DNS server queries.

## Prerequisites

Before running the DNS Proxy Server, make sure you have the following:

1. Python 3 installed on your system.
2. The `config.json` file configured with the desired cache expiration time and external DNS servers.

## Installation

1. Clone the repository or download the source code files.
2. Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

## Configuration

The DNS Proxy Server requires a `config.json` file to be present in the same directory as the source code files. The `config.json` file should have the following structure:

```json
{
  "cache-expiration-time": 300,
  "external-dns-servers": [
    "8.8.8.8",
    "8.8.4.4"
  ]
}
```

- `cache-expiration-time`: The duration in seconds after which cached DNS responses expire.
- `external-dns-servers`: A list of IP addresses for the external DNS servers to use for DNS resolution.

## Usage

To start the DNS Proxy Server, run the following command:

```bash
python dns_proxy_server.py
```

The server will start listening on port 53. Make sure no other service is already using that port.

## Run with docker

```
docker build -t dns_proxy_server .

docker run --network host -p 53:53 -d dns_proxy_server
```

## Features

### DNS Parsing

The `DNSParser` class provides methods to parse DNS packets and extract relevant information. It includes the following methods:

- `parse_dns_packet(data)`: Parses a DNS packet and returns the transaction ID, flags, question count, question parts, query type, and query class.
- `find_ip_from_response(data)`: Placeholder method to extract the IP address from a DNS response. You need to implement this method.

### DNS Proxy Server

The `DNSProxyServer` class implements the DNS proxy server functionality. It includes the following methods:

- `start_dns_proxy()`: Starts the DNS proxy server and listens for incoming DNS queries.
- `construct_dns_response(transaction_id, flags, question_count, queries, query_type, query_class, ip)`: Constructs a DNS response packet with the provided information.
- `create_answer_section(query_type, query_class, answer)`: Creates the answer section of a DNS response packet.
- `ip_to_bytes(ip)`: Converts an IP address from string format to bytes.

### DNS Resolver

The `DNSResolver` class handles DNS resolution by querying external DNS servers. It includes the following methods:

- `resolve_dns(domain, data)`: Resolves a DNS query by sending it to external DNS servers. It checks the cache first and returns the result. If not found in the cache, it queries the external DNS servers and updates the cache with the response.

## Customization

You can customize the DNS Proxy Server by modifying the `DNSProxyServer` and `DNSResolver` classes according to your requirements. For example, you can implement the `find_ip_from_response` method in the `DNSParser` class to extract the IP address from a DNS response.


## Authors

- Erfan Parifard
- Ahmadreza Enayati
