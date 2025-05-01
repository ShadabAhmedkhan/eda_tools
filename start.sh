#!/bin/bash
apt-get update && apt-get install -y wkhtmltopdf
uvicorn main:app --host=0.0.0.0 --port=10000
