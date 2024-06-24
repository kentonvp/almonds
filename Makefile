ENV_FILE:=.env

.PHONY: app pre-commit

app:
	env `cat ${ENV_FILE} | grep -v "#" | xargs` poetry run python src/run.py


pre-commit:
	poetry run isort . && poetry run black .
