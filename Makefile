.PHONY: run run_http run_worker run_test

run:
	./start_healthcheck_and_model_engine.sh

run_http:
	uvicorn main:app --host 0.0.0.0 --reload

run_worker:
	python run.py

run_test:
	python -m unittest discover .