# Pipeline

This folder contains all code and resources required for the pipeline.

## Environment

Create a `.env` file at the project root with the following variables:

```sh
DATABASE_NAME=XXXXXXXXX
DATABASE_NAME_INITIAL=XXXXXXXXX
```

## Set-up and installation instructions

1. Create venv `python3 -m venv venv`
2. Activate venv `source .\venv\bin\activate`
3. Install Requirements `pip install -r requirements.txt`

## Development Instructions

- Run `python3 pipeline.py`

## Documentation

Database Format Below

| example |
| :-----: | ---- | ---- | ------- |
| serial  | date | text | decimal |
