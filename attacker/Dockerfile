FROM ubuntu:24.04

RUN apt-get update && \
    apt-get install -y curl nmap iputils-ping && \
    rm -rf /var/lib/apt/lists/*

CMD ["bash"]
