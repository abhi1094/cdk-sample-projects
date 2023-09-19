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
        python3 python3-pip && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:${PATH}"


# # Download and install Python 3.9 from source
# RUN wget https://www.python.org/ftp/python/3.9.6/Python-3.9.6.tgz && \
#     tar -xf Python-3.9.6.tgz && \
#     cd Python-3.9.6 && \
#     ./configure && \
#     make && \
#     make install

# # Install pip for Python 3.9
# RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
#     python3.9 get-pip.py && \
#     rm get-pip.py

# # Clean up
# RUN apt-get clean && \
#     rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
#     rm -rf Python-3.9.6*

ARG BUILD_PATH=/data  
ARG AWS_TARGET_ACCOUNT
ARG BRANCH_NAME 
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY 
ARG AWS_SESSION_TOKEN

# RUN python3 -m venv .venv
# RUN . .venv/bin/activate
RUN python3 -V

COPY data-glue-canbus-message.json .

COPY e2e_wrapper_canbus_message.py .

COPY dev-requirements.txt .

RUN pip install -r dev-requirements.txt -q

CMD ["python3", "-u", "e2e_wrapper_canbus_message.py"]
