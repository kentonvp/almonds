ENV_FILE:=.env

.PHONY: app

app:
	env `cat ${ENV_FILE} | grep -v "#" | xargs` poetry run python src/run.py
