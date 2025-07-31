FROM python:3.10-slim

# Prevents .pyc files & ensures stdout logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=2.1.3
ENV POETRY_HTTP_TIMEOUT=300

# System dependencies
RUN apt-get update && apt-get install -y \
    curl build-essential libssl-dev libffi-dev git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Set workdir
WORKDIR /app

COPY . .
# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

# Copy the rest of the codebase including app/ and data/


# Create the `data/` folder if it doesn't exist
RUN mkdir -p /app/data

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

