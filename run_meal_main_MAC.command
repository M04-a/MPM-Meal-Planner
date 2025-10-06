#!/bin/bash
cd "$(dirname "$0")/meal"
source ../.venv/bin/activate
python3 -m uvicorn api.api_run:app --reload --host 0.0.0.0 --port 8000; exec $SHELL

