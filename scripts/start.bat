@echo off
setlocal

echo Starting Social Scraper (Docker Compose)...

docker-compose build
if errorlevel 1 goto :error

docker-compose up -d
if errorlevel 1 goto :error

echo Done. Services:
docker-compose ps

goto :eof

:error
echo Failed to start services.
exit /b 1
