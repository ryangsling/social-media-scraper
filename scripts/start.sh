#!/usr/bin/env sh
set -e

echo "Starting Social Scraper (Docker Compose)..."

docker-compose build
docker-compose up -d

echo "Done. Services:"
docker-compose ps
