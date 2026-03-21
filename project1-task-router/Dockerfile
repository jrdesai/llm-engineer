FROM python:3.12-slim

WORKDIR /app

# Copy requirements first (Docker layer caching — don't rebuild deps unless they change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code after (changes to code don't bust the deps layer)
COPY . .

# Don't run as root in containers — security best practice
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
