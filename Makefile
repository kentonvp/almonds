ENV_FILE:=.env

.PHONY: app format pre-commit tests

app:
	env `cat ${ENV_FILE} | grep -v "#" | xargs` poetry run python src/run.py

format:
	poetry run isort . && poetry run black .

pre-commit: format tests

tests:
	poetry run pytest
