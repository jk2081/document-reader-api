FROM python:3.11

WORKDIR /app

# Copy wheel file and requirements
COPY ../document-reader/dist/document_reader-0.3.0-py3-none-any.whl /tmp/
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for local storage
RUN mkdir -p /app/data

# Simple health check
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]