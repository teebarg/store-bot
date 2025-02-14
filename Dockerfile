FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /app/

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Place executables in the environment at the front of the path
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/app/.venv/bin:$PATH"

# Compile bytecode
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

# Install dependencies
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

ENV PYTHONPATH=/app

COPY ./scripts /app/scripts

COPY ./pyproject.toml ./uv.lock ./alembic.ini /app/

COPY ./app /app/app

# Sync the project
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

CMD ["fastapi", "run", "--workers", "4", "app/main.py"]


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




# # Build stage
# FROM python:3.9-slim as builder

# # Set working directory
# WORKDIR /app

# # Install build dependencies and Python packages
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# # Upgrade pip and install requirements
# COPY requirements.txt .
# RUN pip install --upgrade pip && \
#     pip install --no-cache-dir -r requirements.txt

# # Copy project files
# COPY ./pyproject.toml ./alembic.ini ./
# COPY ./scripts ./scripts
# COPY ./app ./app

# # Production stage
# FROM python:3.9-slim

# # Set working directory
# WORKDIR /app

# # Set environment variables
# ENV PYTHONPATH=/app

# # Install runtime dependencies
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#     libgomp1 \
#     && rm -rf /var/lib/apt/lists/*

# # Copy only necessary files from builder
# COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
# COPY --from=builder /app/scripts ./scripts
# COPY --from=builder /app/pyproject.toml /app/alembic.ini ./
# COPY --from=builder /app/app ./app

# # Expose the port
# EXPOSE 8000

# # Run the application
# CMD ["fastapi", "run", "--workers", "4", "app/main.py"]
