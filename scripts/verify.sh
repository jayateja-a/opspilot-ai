#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose up --build -d --wait --wait-timeout 300
docker compose --profile test run --build --rm tests
