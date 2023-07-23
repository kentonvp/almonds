.PHONY: run console

run:
	poetry run textual run --dev src/almonds/ui/app.py

console:
	poetry run textual console
