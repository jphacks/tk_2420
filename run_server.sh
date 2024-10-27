#!/bin/bash
set -euo pipefail

cd /home/jphack24/tk_2420
source .venv/bin/activate
cd  ./project2

if lsof -i :5000; then
    echo "Port 5000 is already in use"
else
    flask run --host=0.0.0.0 --port 5000
fi