import time
import os
import matplotlib.pyplot as plt
import numpy as np
import psutil


def get_traffic():
    traffic_sent = 0
    traffic_received = 0
    for interface in psutil.net_io_counters(pernic=True).values():
        traffic_sent += interface.bytes_sent
        traffic_received += interface.bytes_recv

    return traffic_sent, traffic_received


def request_to_dns_server(request_domain, dns_server):
    start_time = time.time()
    command = "nslookup " + request_domain + f" {dns_server}"
    traffic_sent_0, traffic_received_0 = get_traffic()

    result = os.popen(command)
    output = result.read()
    end_time = time.time()
    result.close()
    print(request_domain + " done!")

    traffic_sent_1, traffic_received_1 = get_traffic()

    out_traffic = traffic_sent_1 - traffic_sent_0
    in_traffic = traffic_received_1 - traffic_received_0

    return (end_time - start_time), (out_traffic, in_traffic)


# Run a shell command
requestsList = ["google.com", "stackoverflow.com", "gmail.com", "vc.kntu.ac.ir", "varzesh3.com", "quera.org",
                "golestan.kntu.ac.ir", "typingclub.com", "w3schools.com", "javatpoint.com"]

benchmark_data_other_server = []
traffic_other_server = []
print("Start requesting through google dns server...")
for num in range(0, 10):
    req = request_to_dns_server(requestsList[num % 10], "8.8.8.8")
    benchmark_data_other_server.append(req[0])
    traffic_other_server.append(req[1])
print(">>> Finished requesting through google dns server")

benchmark_data_our_server = []
traffic_our_server = []
print("Start requesting through our dns server...")
for num in range(0, 10):
    req = request_to_dns_server(requestsList[num % 10], "127.0.0.1")
    benchmark_data_our_server.append(req[0])
    traffic_our_server.append(req[1])
print(">>> Finished requesting through our dns server")

print(f"incoming traffic saved: {sum([i[1] for i in traffic_our_server]) - sum([i[1] for i in traffic_other_server])}")
print(f"outgoing traffic saved: {sum([i[0] for i in traffic_our_server]) - sum([i[0] for i in traffic_other_server])}")

# Generate x-axis values
x_values = np.arange(len(benchmark_data_other_server))
# Plot the bar graph
bar_width = 0.35

# Plot the bar graph
plt.bar(x_values, benchmark_data_other_server, width=bar_width, label='Google DNS')
plt.bar(x_values + bar_width, benchmark_data_our_server, width=bar_width, label='Our DNS')


# Add labels and title
plt.xlabel('Request number')
plt.ylabel('Time elapsed')
plt.title('Benchmark')

# Save the graph
plt.savefig('bar_graph.png')
