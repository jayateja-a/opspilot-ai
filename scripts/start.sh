#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; fi
docker compose up --build -d --wait --wait-timeout 300
echo "OpsPilot AI is ready: http://localhost:3000"
echo "Swagger: http://localhost:8080/swagger-ui/index.html"
