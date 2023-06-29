import time
import os
import matplotlib.pyplot as plt
import numpy as np


def request_to_dns_server(request_domain, dns_server):
    start_time = time.time()
    command = "nslookup " + request_domain + f" {dns_server}"
    result = os.popen(command)
    output = result.read()
    end_time = time.time()
    result.close()
    return end_time - start_time


# Run a shell command
requestsList = ["google.com", "stackoverflow.com", "gmail.com", "vc.kntu.ac.ir", "varzesh3.com", "quera.org",
                "golestan.kntu.ac.ir", "typingclub.com", "w3schools.com", "javatpoint.com"]

benchmark_data_other_server = []
print("Start requesting through google dns server...")
for num in range(0, 100):
    benchmark_data_other_server.append(request_to_dns_server(requestsList[num % 10], "8.8.8.8"))
print(">>> Finished requesting through google dns server")

benchmark_data_our_server = []
print("Start requesting through our dns server...")
for num in range(0, 100):
    benchmark_data_our_server.append(request_to_dns_server(requestsList[num % 10], "127.0.0.1"))
print(">>> Finished requesting through our dns server")


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
