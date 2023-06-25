import datetime
import socket

cache = {}

print('Enter domains. type `exit` to exit')
while True:
    print('>', end='')
    input_text = input()

    if input_text == 'exit':
        break

    EXPIRATION_TIME_SECONDS = 5
    if cache.get(input_text) and (datetime.datetime.now().timestamp() - cache[input_text][1]) <= EXPIRATION_TIME_SECONDS:
        print(f'{cache[input_text][0]} // cache hit')
        continue

    try:
        ip = socket.gethostbyname(input_text)
        resolution_time = datetime.datetime.now().timestamp()
        cache[input_text] = (ip, resolution_time)

        print(f'{ip} // cache miss')
    except Exception as e:
        print(f'resolver error : {e}')
