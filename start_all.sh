#!/bin/bash

case "$ROLE" in
    server)
        # Your command to start the worker goes here
        echo "Starting webserver..."
        # Example: celery -A proj worker
        uvicorn main:app --host 0.0.0.0 --port ${PRESTO_PORT} --reload
        ;;

    worker)
        # Your command to start the worker goes here
        echo "Starting worker..."
        # Example: celery -A proj worker
        python run_worker.py &
        python run_processor.py
        ;;
esac

