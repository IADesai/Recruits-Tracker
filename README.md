# personal-finances-db

A dashboard for my personal finances

## Set-up and installation instructions

1. Create venv `python3 -m venv venv`
2. Activate venv `source .\venv\bin\activate`
3. Install Requirements `pip install -r requirements.txt`

## Documentation

Database Format Below

| transaction_id | transaction_date | transaction_description | transaction_value | transaction_type |
| :------------: | :--------------: | :---------------------: | :---------------: | :--------------: |
|     serial     |       date       |          text           |      decimal      |       text       |
