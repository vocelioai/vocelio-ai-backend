FROM python:3.11-slim

WORKDIR /app

COPY ../../apps /app/apps
COPY ../../shared /app/shared
COPY apps/settings/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8017

CMD ["python", "apps/settings/src/main.py"]
