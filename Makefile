.PHONY: app test

app:
	dotenvx run -- python src/run.py

test:
	pytest --cov -v
