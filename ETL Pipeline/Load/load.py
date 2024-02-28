"""This module contains functions used to create and load the database."""
from psycopg2 import connect, extensions, Error
from psycopg2.extensions import connection
import psycopg2.extras
import pandas as pd
from datetime import datetime, timedelta
import sys
import urllib.parse as up
from os import environ
from dotenv import load_dotenv


load_dotenv()
config = environ


def create_database():
    """Creates the database"""
    conn_initial = connect(
        database=config["DATABASE_NAME_INITIAL"]
    )
    auto_commit = extensions.ISOLATION_LEVEL_AUTOCOMMIT
    conn_initial.set_isolation_level(auto_commit)
    # Create a cursor to execute commands
    # We use the RealDictCursor so that we can get the results as a dictionary
    cur = conn_initial.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(str(open("schema.sql", "r").read()[0:34]))
    cur.execute(str(open("schema.sql", "r").read()[34:61]))
    cur.close()
    conn_initial.commit()
    conn_initial.close()


def create_tables(conn_database: connection):
    """Creates the finances table in database"""
    cur = conn_database.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(str(open("schema.sql", "r").read()[61:]))
    cur.close()
    conn_database.commit()


def populate_database(conn_current: connection):
    """Populates the database"""
    recruit2023_df = pd.read_csv(f"ExcelSheets/2023Recruits.csv", index_col=False)
    recruit2024_df = pd.read_csv(f"ExcelSheets/2024Recruits.csv", index_col=False)
    df = pd.concat([recruit2024_df[1:]])
    df = df.dropna(subset=['Advisor name'])
    date_columns = ['Start Date', 'Newcomer demo']
    df[date_columns] = df[date_columns].applymap(lambda x: pd.to_datetime(x, errors='coerce').strftime('%Y-%m-%d') if pd.notna(x) else x)
    
    dates_df = pd.read_excel(f"ExcelSheets/TRAINING AND REPORTING DATES 2024.xlsx", index_col=False, skiprows=3)[:-1]

    team_leaders = {"Miranda Quantrill","Ana Maria Lumina","Judi Hampton","Malgorzata Strzelecka","Alina Matei","Sara Joiner-Jarrett"}

    cur = conn_current.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    for index, row in dates_df.iterrows():
        cur.execute(f'INSERT INTO calendar_dates(training_date, start_date, thirty_days, ninety_days, one_eighty_days) VALUES \
                (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING', (row[0], row[3], row[4], row[5], row[5] + timedelta(days=90)))
    cur.close()
    conn_current.commit()

    cur = conn_current.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    for index, row in df.iterrows():
        if row[0] in team_leaders:
            role = 1
        else:
            role = 2

        select_query = "SELECT training_date_id FROM calendar_dates WHERE training_date LIKE %s;"
        cur.execute(select_query, ("%" + row[4].upper().rstrip() + "%",))
        result = cur.fetchone()

        if result:
            training_date_id_fk_value = result['training_date_id']
        else:
            training_date_id_fk_value = 0

        cur.execute('INSERT INTO members(name, role_id_fk) VALUES (%s, %s) ON CONFLICT DO NOTHING', (row[0], role))

        select_query = "SELECT member_id FROM members WHERE name LIKE %s;"
        cur.execute(select_query, ('%' + row[0] + '%',))
        result = cur.fetchone()

        if result:
            member_id_details_fk_value = result['member_id']

        cur.execute('INSERT INTO member_details(member_id_details_fk, purchase, training_date_id_fk) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING', (member_id_details_fk_value, row[1], training_date_id_fk_value))
        row[9:18] = [None if pd.isna(val) else val for val in row[9:18]]

        cur.execute('INSERT INTO member_sales(member_id_fk, newcomer_demo, first_sale, second_sale, third_sale, fourth_sale, fifth_sale, sixth_sale, seventh_sale, eighth_sale) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING', (member_id_details_fk_value, row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17]))

        select_query = "SELECT member_id FROM members WHERE name LIKE %s;"
        cur.execute(select_query, ('%' + row[2] + '%',))
        result = cur.fetchone()
        if result:
            team_leader_id_value = result['member_id']

        if type(row[3]) is float:
            recruiting_advisor_id_value = None
        else:
            select_query = "SELECT member_id FROM members WHERE name LIKE %s;"
            cur.execute(select_query, ('%' + row[3] + '%',))
            result = cur.fetchone()
            if result:
                recruiting_advisor_id_value = result['member_id']
            else:
                cur.execute('INSERT INTO members(name, role_id_fk) VALUES (%s, %s) ON CONFLICT DO NOTHING', (row[3], 2))
                select_query = "SELECT member_id FROM members WHERE name LIKE %s;"
                cur.execute(select_query, ('%' + row[3] + '%',))
                result = cur.fetchone()
                recruiting_advisor_id_value = result['member_id']
        cur.execute('INSERT INTO member_relationships(member_relationship_id_fk, team_leader_id, recruiting_advisor_id) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING', (member_id_details_fk_value, team_leader_id_value, recruiting_advisor_id_value))


    cur.close()
    conn_current.commit()


def get_db_connection():   # pragma: no cover
    """Establishes a connection with the PostgreSQL database."""
    try:
        up.uses_netloc.append("postgres")
        url = up.urlparse(environ["DATABASE_URL"])
        conn = psycopg2.connect(database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
        )
        print("Database connection established successfully.")
        return conn
    except Error as err:
        print("Error connecting to database: ", err)
        sys.exit()


if __name__ == "__main__":
    # create_database()
    
    conn_thermomix = get_db_connection()
    
    create_tables(conn_thermomix)
    populate_database(conn_thermomix)