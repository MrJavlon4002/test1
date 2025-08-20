FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# tzdata for ZoneInfo, curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
      tzdata curl ca-certificates gnupg \
    && rm -rf /var/lib/apt/lists/*

# Node 18 only needed if you later enable Airbnb MCP with npx
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
 && apt-get install -y --no-install-recommends nodejs \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8081
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8081"]
