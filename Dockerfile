# FROM python:3.9
# FROM python:3.9-slim
FROM beafdocker/chat-image:latest

# Set working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

COPY ./scripts /app/scripts

COPY ./pyproject.toml ./alembic.ini /app/

COPY ./app /app/app

# Expose the port on which FastAPI runs
EXPOSE 8000

# Run the application using Uvicorn (FastAPI’s recommended ASGI server)
CMD ["fastapi", "run", "--workers", "4", "app/main.py"]
