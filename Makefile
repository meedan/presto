.PHONY: run run_http run_worker run_processor run_test

run:
	./start_all.sh

run_http:
	uvicorn main:app --host 0.0.0.0

run_worker:
	python run_worker.py

run_processor:
	python run_processor.py

run_test:
	python -m pytest test
