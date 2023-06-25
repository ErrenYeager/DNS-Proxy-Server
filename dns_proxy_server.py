import datetime
import socket

cache = {}


def resolve_dns(input_text):
    expiration_time_seconds = 5
    if cache.get(input_text) and (datetime.datetime.now().timestamp() - cache[input_text][1]) <= expiration_time_seconds:
        return cache[input_text][0], True  # Return cached IP and cache hit status

    try:
        ip = socket.gethostbyname(input_text)
        resolution_time = datetime.datetime.now().timestamp()
        cache[input_text] = (ip, resolution_time)
        return ip, False  # Return resolved IP and cache miss status
    except Exception as e:
        return str(e), False  # Return error message and cache miss status


def start_dns_proxy():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost', 53))  # Bind to the DNS port (53)

    print('DNS proxy server started. Listening on port 53...')

    while True:
        data, client_address = server_socket.recvfrom(1024)
        print(client_address)
        request_domain = data.decode().strip()

        if request_domain == 'exit':
            break

        ip, cache_hit = resolve_dns(request_domain)

        response = f'{ip}\n' if not isinstance(ip, str) else f'Error: {ip}\n'
        server_socket.sendto(response.encode(), client_address)
        print(f'Resolved: {request_domain} => {response.strip()} (Cache {"hit" if cache_hit else "miss"})')

    server_socket.close()


if __name__ == '__main__':
    start_dns_proxy()
