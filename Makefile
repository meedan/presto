.PHONY: run run_http run_worker run_processor run_test

run:
	./start_all.sh

run_http:
ifeq ($(filter $(DEPLOY_ENV),qa live),)
	uvicorn main:app --host 0.0.0.0 --reload
else
	uvicorn main:app --host 0.0.0.0
endif

run_worker:
	python run_worker.py

run_processor:
	python run_processor.py

run_test:
	python -m pytest test
