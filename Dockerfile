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
        sqlite3

# Download and install Python 3.9 from source
RUN wget https://www.python.org/ftp/python/3.9.6/Python-3.9.6.tgz && \
    tar -xf Python-3.9.6.tgz && \
    cd Python-3.9.6 && \
    ./configure && \
    make && \
    make install

# Install pip for Python 3.9
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.9 get-pip.py && \
    rm get-pip.py

# Clean up
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    rm -rf Python-3.9.6*

# Set working directory
WORKDIR /app

# Run your command or script here
CMD ["/bin/bash"]
