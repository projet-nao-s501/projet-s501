FROM python:3.11.2-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    nano \
    cmake \
    iproute2 \
    iputils-ping \
    zip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app/

RUN python3 -m venv venv
RUN /app/venv/bin/pip install --upgrade pip
RUN /app/venv/bin/pip install -r requirements.txt
