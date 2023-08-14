.PHONY: run run_http run_worker run_test

run: 
	uvicorn main:app --reload &
	python run.py &
	wait

run_http:
	uvicorn main:app --reload

run_worker:
	python run.py

run_test:
	python -m unittest discover .