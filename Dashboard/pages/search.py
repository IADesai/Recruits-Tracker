"""Streamlit dashboard application code"""
from psycopg2 import connect, Error
from psycopg2.extensions import connection
import streamlit as st
import pandas as pd
import sys
import urllib.parse as up
from os import environ
from dotenv import load_dotenv

load_dotenv()
config = environ

def get_data(conn: connection) -> pd.DataFrame:
    """Function that gets the required data from the database connection"""
    cursor = conn.cursor()
    cursor.execute("SELECT \
  m.member_id, \
  m.name AS member_name, \
  tl.name AS team_leader_name, \
  ra.name AS recruiting_advisor_name, \
  r.role_name, \
  md.purchase, \
  cd.training_date, \
  cd.start_date, \
  cd.thirty_days, \
  cd.ninety_days, \
  cd.one_eighty_days, \
  ms.newcomer_demo, \
  ms.first_sale, \
  ms.second_sale, \
  ms.third_sale, \
  ms.fourth_sale, \
  ms.fifth_sale, \
  ms.sixth_sale, \
  ms.seventh_sale, \
  ms.eighth_sale \
FROM \
  members m \
JOIN \
  roles r ON m.role_id_fk = r.role_id \
LEFT JOIN \
  member_details md ON m.member_id = md.member_id_details_fk \
LEFT JOIN \
  calendar_dates cd ON md.training_date_id_fk = cd.training_date_id \
LEFT JOIN \
  member_sales ms ON m.member_id = ms.member_id_fk \
LEFT JOIN \
  member_relationships mr ON m.member_id = mr.member_relationship_id_fk \
LEFT JOIN \
  members tl ON mr.team_leader_id = tl.member_id \
LEFT JOIN \
  members ra ON mr.recruiting_advisor_id = ra.member_id \
ORDER BY team_leader_name, role_name;")
    rows = cursor.fetchall()
    live_dataframe = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
    cursor.execute("SELECT * FROM calendar_dates WHERE training_date_id > 0;")
    rows = cursor.fetchall()
    calendar_dataframe = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
    cursor.execute("SELECT name FROM members WHERE role_id_fk = 1;")
    rows = cursor.fetchall()
    team_leader_dataframe = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
    cursor.close()
    conn.close()
    return live_dataframe, calendar_dataframe, team_leader_dataframe


def dashboard_header() -> None:
    """Creates a header for the dashboard and title on tab."""

    st.markdown("<h1 style='text-align: center; color: white;'>Recruits Search</h1>", unsafe_allow_html=True)


def sidebar() -> int:
    """Sidebar for the streamlit dashboard, with interactive buttons"""
    if "start_index" not in st.session_state:
        st.session_state.start_index = 0
    st.sidebar.markdown("<h1 style='text-align: center; color: white;'>Thermomix Recruits Tracker</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("An app for helping you track your thermomix recruits")
    st.sidebar.title("Options & Filters Menu")
    st.sidebar.page_link("streamlit.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/insertions.py", label="Add/Remove Recruit", icon="📝")
    st.sidebar.page_link("pages/edit.py", label="Edit Recruit Information", icon="✍️")
    st.sidebar.page_link("pages/update.py", label="Update Recruit Sales Info/Dates", icon="📅")
    st.sidebar.page_link("pages/search.py", label="Recruit Search", icon="🔍")


def on_toggle_or_archive_change() -> None:
    """Sets the index back to 0 for all of the graphs upon changing
    the toggle status or which archive is being viewed.
    """
    st.session_state.start_index = 0


def create_tables(data: pd.DataFrame, cal_data: pd.DataFrame, team_leader_data: pd.DataFrame) -> None:
  """creates main table"""
  unique_member_names = data['member_name'].unique()
  selected_member_name = st.text_input('Search for Member Name (Please press Enter to apply)', '')
  filtered_data_df = data[data['member_name'].str.contains(selected_member_name, case=False)]
  st.dataframe(filtered_data_df, hide_index=True, use_container_width=True)

  st.markdown("<h1 style='text-align: center;'>Calendar Table</h1>", unsafe_allow_html=True)
  cal_data['start_year'] = pd.to_datetime(cal_data['start_date']).dt.year
  unique_years = cal_data['start_year'].unique()
  selected_year = st.selectbox('Select Year', unique_years)
  filtered_df = cal_data[cal_data['start_year'] == selected_year].drop(columns=['start_year', 'training_date_id'])
  st.dataframe(filtered_df, hide_index=True, use_container_width=True)


def get_db_connection():   # pragma: no cover
    """Establishes a connection with the PostgreSQL database."""
    try:
        up.uses_netloc.append("postgres")
        url = up.urlparse(st.secrets.db_credentials.url)
        conn = connect(database=url.path[1:],
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

  st.set_page_config(page_title="Thermomix Recruits Tracker", layout="wide")

  custom_css = """
  <style>
  [data-testid="stSidebarNav"] {
      display: none;
  }
  </style>
  """
  st.markdown(custom_css, unsafe_allow_html=True)

  dashboard_header()
  sidebar()

  conn_thermomix = get_db_connection()

  live_df, calendar, team_leaders = get_data(conn_thermomix)

  create_tables(live_df, calendar, team_leaders)
