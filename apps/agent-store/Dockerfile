FROM python:3.11-slim

WORKDIR /app

COPY ../../apps /app/apps
COPY ../../shared /app/shared
COPY apps/agent-store/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8023

CMD ["python", "apps/agent-store/src/main.py"]
