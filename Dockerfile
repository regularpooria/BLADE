FROM python:3.9-bullseye

# Install common build tools (optional but safe)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libyaml-dev \
    && rm -rf /var/lib/apt/lists/*
