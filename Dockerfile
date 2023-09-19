# Use the official Ubuntu base image
FROM ubuntu:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        zlib1g-dev \
        libncurses5-dev \
        libgdbm-dev \
        libnss3-dev \
        libssl-dev \
        libreadline-dev \
        libffi-dev \
        curl \
        wget \
        git \
        awscli \
        jq \
        nodejs \
        npm \
        python3 python3-pip python3-venv && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:${PATH}"

# Create a virtual environment and activate it
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Now you can install Python packages using pip
COPY dev-requirements.txt .
RUN pip install -r dev-requirements.txt -q

# Copy your application into the container
COPY data-glue-canbus-message.json .
COPY e2e_wrapper_canbus_message.py .

CMD ["python3", "-u", "e2e_wrapper_canbus_message.py"]
