# almonds

Personal Finance App


## Project Setup

1. Copy `example.env` to `.env` and populate
```bash
$ cp example.env .env
```

2. Make virtual environment
```bash
$ python -m venv .venv
```

3. Activate virtual environment
```bash
$ source .venv/bin/activate
```

4. Install dependencies
```bash
$ pip install '.[dev]'
```

5. (optional) Migrate database if necessary. Look in `src/almonds/sql/` for migration scripts.
```bash
$ sqlite3 almonds.db < src/almonds/sql/file.sql
```

6. Run the app
```bash
$ make app
```

7. Open in a browser: `http://127.0.0.1:5000`


![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/kentonvp/1898a7f66ccef8dab95271b327e55aa7/raw/covbadge.json)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
