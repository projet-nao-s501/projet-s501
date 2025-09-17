FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    nano \
    cmake \
    libpython3-dev \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app/

RUN python3 -m venv venv
RUN /app/venv/bin/pip install --upgrade pip