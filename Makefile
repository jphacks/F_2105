SHELL = "/bin/bash"
default:
	source .venv/bin/activate
	cd system && python app.py

init: 
	source .venv/bin/activate
	pip install -r system/requirements.txt
	cd system
	python app.py

