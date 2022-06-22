#!/bin/sh

set -e

exec gunicorn --bind 0.0.0.0:5000 -k uvicorn.workers.UvicornWorker main:app
