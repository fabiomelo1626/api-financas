#!/bin/bash
cd /root/api-instituto
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 6000
