.PHONY: build serve publications

build: publications
	hugo --minify

serve: publications
	hugo server

publications:
	python3 scripts/bibtex_to_json.py
