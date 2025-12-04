FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements-groq.txt .
RUN pip install --no-cache-dir -r requirements-groq.txt && \
    pip install --no-cache-dir --ignore-installed cffi cryptography

# Copy application
COPY . .

# Create data directory for SQLite
RUN mkdir -p /app/data

# Run the bot
CMD ["python", "main.py"]
