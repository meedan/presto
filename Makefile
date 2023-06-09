.PHONY: run run_http run_worker run_test

run: $(if $(filter http,$(RUN_MODE)),run_http,run_worker)

run_http:
	uvicorn main:app --reload

run_worker:
	python run.py

run_test:
	python -m unittest discover .