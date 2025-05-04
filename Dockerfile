FROM python:3.10.14-bookworm

# Install all OS-level dependencies in one go
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      git \
      wget \
      pv \
      jq \
      python3-dev \
      libssl-dev \
      poppler-utils \
      mediainfo \
      aria2 \
      ffmpeg \
      curl \
      unzip && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy your application code and ensure downloads folder exists
COPY . .
RUN mkdir -p downloads

# Keep your original CMD exactly as is
CMD gunicorn app:app & python3 main.py
