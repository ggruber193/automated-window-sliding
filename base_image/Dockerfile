FROM debian:bookworm-slim


RUN apt update && apt install -y procps python3 python3-pip && rm -rf /var/lib/apt/lists/* && \
pip install dendropy biopython --no-cache-dir --break-system-packages && \
apt remove python3-pip -y && apt autoremove -y && apt clean autoclean

# TODO setup quay.io build trigger 