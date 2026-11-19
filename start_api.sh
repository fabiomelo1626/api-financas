#!/bin/bash
cd /root/api-financas
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 5500
