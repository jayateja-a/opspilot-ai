FROM python:3.12-slim
WORKDIR /workspace
RUN pip install --no-cache-dir pytest==8.3.5 httpx==0.28.1
COPY scripts/e2e_test.py scripts/e2e_test.py
COPY lab/app.py lab/app.py
COPY lab/test_lab.py lab/test_lab.py
COPY lab/test_commerce.py lab/test_commerce.py
COPY lab/commerce_lab.py lab/commerce_lab.py
COPY fixtures/incidents.json fixtures/incidents.json
