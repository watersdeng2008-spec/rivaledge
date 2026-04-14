# RivalEdge Backend — Railway-ready Dockerfile — build v4
FROM mcr.microsoft.com/playwright:v1.49.0-jammy

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Playwright browsers already included in base image
# Skip redundant install to avoid build failures

# Force fresh copy of ALL application code
# This layer should never be cached when code changes
ARG CACHE_BUST=15
COPY . /app/

# Expose port
EXPOSE 8000

# Run the app with uvicorn
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port \${PORT:-8000}"
