.PHONY: lint fix_lint tests

lint:
	ruff check .
	ruff format --check .

fix_lint:
	ruff check . --fix
	ruff format .

tests:
	pytest -vv
