
# remove all files
.PHONY: clean
clean:
	rm -rf venv

# create virtual environment
venv:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt

# generate recurrence files
.PHONY: generate
generate: venv
	venv/bin/python3 generate.py