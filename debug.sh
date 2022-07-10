#!/bin/sh
docker run --rm -p 8080:8080 -e PORT=8080 -v `pwd`/app:/app links python3 /app/main.py
