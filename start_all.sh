#!/bin/sh

# Start the first process in the background
uvicorn main:app --host 0.0.0.0 --port ${PRESTO_PORT} --reload &

# Start the second process in the foreground
NUM_WORKERS=${NUM_WORKERS:-1}  # Default to 1 worker if not specified

for i in $(seq 1 $NUM_WORKERS)
do
  (
    while true; do
      echo "Starting run_worker.py instance $i..."
      python run_worker.py worker-$i
      echo "run_worker.py instance $i exited. Restarting..."
      sleep 30  # Prevent potential rapid restart loop
    done
  ) &.  # run workers as background processes
done

python run_processor.py