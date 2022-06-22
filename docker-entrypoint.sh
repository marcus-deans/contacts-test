#!/bin/sh

set -e

exec gunicorn -k uvicorn.workers.UvicornWorker main:app
