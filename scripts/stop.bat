@echo off
setlocal

echo Stopping Social Scraper (Docker Compose)...

docker-compose down
if errorlevel 1 goto :error

echo Stopped.

goto :eof

:error
echo Failed to stop services.
exit /b 1
