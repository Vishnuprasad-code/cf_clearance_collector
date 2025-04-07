#!/bin/bash
# alias python=python3
rm -rf /tmp/.X99-lock
Xvfb :99 -screen 0 640x480x8 -nolisten tcp &
export DISPLAY=:99
# gunicorn app.run:main --bind 0.0.0.0:8080 --max-requests 200 --worker-class aiohttp.GunicornWebWorker
uvicorn app.run:app --reload --host 0.0.0.0
# python app/run.py
