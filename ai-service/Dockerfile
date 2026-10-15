FROM python:3.12-slim
WORKDIR /app
COPY ai-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ai-service/app app
COPY ai-service/tests tests
COPY scripts/e2e_test.py e2e/test_workflow.py
COPY fixtures fixtures
ENV FIXTURES_DIR=/app/fixtures PYTHONUNBUFFERED=1
USER 10001
EXPOSE 8000
CMD ["python","-m","uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
