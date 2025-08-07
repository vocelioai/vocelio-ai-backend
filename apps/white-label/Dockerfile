FROM python:3.11-slim
WORKDIR /app
COPY ../../apps /app/apps
COPY ../../shared /app/shared
COPY apps/white-label/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH="/app"
EXPOSE 8022
CMD ["uvicorn", "apps.white-label.src.main:app", "--host", "0.0.0.0", "--port", "8022"]
