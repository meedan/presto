#!/bin/sh
if [ "$ROLE" != "worker" ]; then

  # Start the HTTP server process in the background if not a worker
  uvicorn main:app --host 0.0.0.0 --port ${PRESTO_PORT} --reload &

fi

if [ "$ROLE" = "worker" ]; then
  # Start worker processes
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
    ) &  # Run workers as background processes
  done
fi

# Start the processor process in the foreground
python run_processor.py