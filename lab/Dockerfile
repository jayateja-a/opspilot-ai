FROM python:3.12-slim
WORKDIR /app
COPY fixtures/incidents.json /fixtures/incidents.json
COPY lab/app.py /app/app.py
COPY lab/commerce_lab.py /app/commerce_lab.py
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/
CMD ["python", "/app/app.py"]
