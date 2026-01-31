FROM python:3.9-slim

WORKDIR /app

# Install network tools and enable IP forwarding
RUN apt-get update && apt-get install -y \
    iproute2 \
    iputils-ping \
    net-tools \
    iptables \
    && rm -rf /var/lib/apt/lists/*

# Enable IP forwarding capability
RUN echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf

# Copy all router code
COPY *.py /app/
COPY docker_router.py /app/

# Make scripts executable
RUN chmod +x /app/docker_router.py

CMD ["python", "docker_router.py"]

