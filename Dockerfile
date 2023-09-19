# Use the official Ubuntu 20.04 base image
FROM ubuntu:20.04

# Set environment variables
ENV PYENV_ROOT /root/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
ENV VENV_PATH /app/.venv

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    make build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
    libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl git

# Install Pyenv
RUN curl https://pyenv.run | bash

# Install Python version (change this to the version you need)
RUN pyenv install 3.8.5

# Set the default Python version to use
RUN pyenv global 3.8.5

# Install pip
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python get-pip.py

# Create a virtual environment
RUN python -m venv $VENV_PATH

# Activate the virtual environment
ENV PATH="$VENV_PATH/bin:$PATH"

# Copy the requirements file into the Docker image
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Clean up
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Verify installation
RUN python --version
RUN pip --version
