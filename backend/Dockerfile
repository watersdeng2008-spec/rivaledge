# RivalEdge Backend — Railway-ready Dockerfile — build v3
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

# Cache bust — forces fresh copy of application code
ARG CACHE_BUST=3
# Copy the rest of the application code
COPY . .

# Expose port
EXPOSE 8000

# Run the app with uvicorn
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port \${PORT:-8000}"
