# Specify the base image
FROM python:3.9.17-alpine3.18

USER root

ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy the project files
COPY dns_parser.py .
COPY dns_proxy_server.py .
COPY dns_resolver.py .

EXPOSE 53
# Specify the command to run
CMD ["python", "-u", "dns_proxy_server.py"]