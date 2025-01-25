# Stage 1: Build
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim-bookworm
ENV TZ=Asia/Ho_Chi_Minh

WORKDIR /app

# Install minimal dependencies in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    wget \
    # Firefox dependencies
    firefox-esr \
    libx11-xcb1 \
    libdbus-glib-1-2 \
    xvfb \
    # Clean up in the same layer
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && rm -rf /var/cache/apt/archives/*

# Copy only necessary Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy application code
COPY . .

CMD ["python", "main.py"]