#!/bin/sh

# Start the first process in the background
uvicorn main:app --host 0.0.0.0 --reload &

# Start the second process in the foreground
# This will ensure the script won't exit until this process does
python run_worker.py & 
python run_processor.py