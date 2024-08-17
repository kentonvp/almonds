.PHONY: app test

app:
	dotenvx run -- poetry run python src/run.py

test:
	poetry run pytest --cov -v

