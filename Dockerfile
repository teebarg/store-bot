# # Second stage
# FROM beafdocker/chat-image:latest

# # Set working directory
# WORKDIR /app

# # Copy the requirements file and install dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# ENV PYTHONPATH=/app

# COPY ./scripts /app/scripts

# COPY ./pyproject.toml ./alembic.ini /app/

# COPY ./app /app/app

# # Expose the port on which FastAPI runs
# EXPOSE 8000

# # Run the application using Uvicorn (FastAPI’s recommended ASGI server)
# CMD ["fastapi", "run", "--workers", "4", "app/main.py"]

# Build stage
FROM python:3.9-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies and Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install requirements
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY ./pyproject.toml ./alembic.ini ./
COPY ./scripts ./scripts
COPY ./app ./app

# Production stage
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy only necessary files from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /app/scripts ./scripts
COPY --from=builder /app/pyproject.toml /app/alembic.ini ./
COPY --from=builder /app/app ./app

# Expose the port
EXPOSE 8000

# Run the application
CMD ["fastapi", "run", "--workers", "4", "app/main.py"]
