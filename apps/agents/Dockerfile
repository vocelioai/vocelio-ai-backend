FROM python:3.11-slim
WORKDIR /app
COPY ../../apps /app/apps
COPY ../../shared /app/shared
COPY apps/agents/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH="/app"
EXPOSE 8000
CMD ["uvicorn", "apps.agents.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
