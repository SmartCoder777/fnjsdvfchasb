FROM python:3.10.14-bookworm

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --upgrade pip \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
       poppler-utils \
       git \
       wget \
       pv \
       jq \
       python3-dev \
       ffmpeg \
       mediainfo \
       libssl-dev \
       aria2 \
       curl \
       unzip \
    && pip install -r requirements.txt \
    && playwright install chromium \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . /app

# Entry point: start Flask and bot
CMD gunicorn app:app & python3 main.py
