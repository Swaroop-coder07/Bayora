FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
# Same image doubles as the sandbox: `python -m app.isolation.worker` (see DOCKER_ENABLED)
RUN useradd -m bayora && mkdir -p /app/audit_logs && chown -R bayora /app
USER bayora
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
