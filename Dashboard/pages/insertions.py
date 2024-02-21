"""Streamlit dashboard application code"""
from psycopg2 import connect
from psycopg2.extensions import connection
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
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

    st.markdown("<h1 style='text-align: center; color: white;'>New Recruits Table</h1>", unsafe_allow_html=True)


def sidebar() -> int:
    """Sidebar for the streamlit dashboard, with interactive buttons"""
    if "start_index" not in st.session_state:
        st.session_state.start_index = 0
    st.sidebar.markdown("<h1 style='text-align: center; color: white;'>Thermomix Recruits Tracker</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("An app for helping you track your thermomix recruits")
    st.sidebar.title("Options & Filters Menu")
    st.sidebar.page_link("streamlit.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/search.py", label="Recruit Search", icon="🔍")
    st.sidebar.page_link("pages/insertions.py", label="Add Recruit", icon="➕")


def on_toggle_or_archive_change() -> None:
    """Sets the index back to 0 for all of the graphs upon changing
    the toggle status or which archive is being viewed.
    """
    st.session_state.start_index = 0


def create_inserts(data: pd.DataFrame, cal_data: pd.DataFrame, team_leader_data: pd.DataFrame, conn_insert: connection) -> None:
    """creates main table"""
    st.header("Recruit Information")

    with st.form("insert_recruit_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_recruit_name = st.text_input("Recruit Name")
        with col2:
            new_recruit_purchase = st.selectbox("Recruit Purchase", ["Owner", "Earner"])
        with col3:
            new_recruit_training_date = st.selectbox("Training Date", cal_data["training_date"].unique())
        col4, col5, col6 = st.columns(3)
        with col4:
            cal_data['start_year'] = pd.to_datetime(cal_data['start_date']).dt.year
            unique_years = cal_data['start_year'].unique()
            new_recruit_year = st.selectbox("Calendar Year", unique_years)
        with col5:
            new_recruit_team_leader = st.selectbox("Team Leader", team_leader_data["name"].unique())
        with col6:
            existing_advisors = list(data["member_name"].unique())
            new_recruit_recruiting_advisor = st.selectbox("Recruiting Advisor", existing_advisors)
            st.markdown("If unable to find advisor, please click 'Add New Recruiting Advisor' below")

        submit_recruit = st.form_submit_button("Add Recruit")

    if submit_recruit:
        cursor = conn_insert.cursor()
        # Get training_date_id from calendar_dates table
        new_recruit_year = int(new_recruit_year)
        cursor.execute("SELECT training_date_id FROM calendar_dates WHERE training_date = %s AND EXTRACT(YEAR FROM start_date) = %s",
                   (new_recruit_training_date, new_recruit_year))
        training_date_id = cursor.fetchone()[0]

        # Get team_leader_id from members table
        cursor.execute("SELECT member_id FROM members WHERE name = %s", (new_recruit_team_leader,))
        team_leader_id = cursor.fetchone()[0]

        # Get recruiting_advisor_id from members table
        cursor.execute("SELECT member_id FROM members WHERE name = %s", (new_recruit_recruiting_advisor,))
        recruiting_advisor_id = cursor.fetchone()[0]

        # Insert new recruit into members table
        cursor.execute("INSERT INTO members (name, role_id_fk) VALUES (%s, %s) RETURNING member_id",
                      (new_recruit_name, 2))
        member_id = cursor.fetchone()[0]

        # Insert new recruit details into member_details table
        cursor.execute("INSERT INTO member_details (member_id_details_fk, purchase, training_date_id_fk) VALUES (%s, %s, %s)",
                      (member_id, new_recruit_purchase, training_date_id))

        # Insert new recruit sales into member_sales table
        cursor.execute("INSERT INTO member_sales (member_id_fk) VALUES (%s) RETURNING member_id_fk", (member_id,))
        member_id_fk_sales = cursor.fetchone()[0]

        # Insert sales details into member_sales table
        cursor.execute("UPDATE member_sales SET newcomer_demo = NULL, first_sale = NULL, second_sale = NULL, third_sale = NULL, "
                      "fourth_sale = NULL, fifth_sale = NULL, sixth_sale = NULL, seventh_sale = NULL, eighth_sale = NULL "
                      "WHERE member_id_fk = %s", (member_id_fk_sales,))

        # Insert new recruit relationships into member_relationships table
        cursor.execute("INSERT INTO member_relationships (member_relationship_id_fk, team_leader_id, recruiting_advisor_id) "
                      "VALUES (%s, %s, %s)", (member_id, team_leader_id, recruiting_advisor_id))

        conn_insert.commit()
        cursor.close()
        st.success(f"Recruit {new_recruit_name} added successfully!")

    with st.form("new_advisor_form"):
        new_advisor_name = st.text_input("Enter New Recruiting Advisor Name")
        if st.form_submit_button("Add New Recruiting Advisor"):
            cursor = conn_insert.cursor()

            # Insert new advisor into members table
            cursor.execute("INSERT INTO members (name, role_id_fk) VALUES (%s, %s)",
                          (new_advisor_name, 2))

            conn_insert.commit()
            cursor.close()
            st.success(f"New advisor {new_advisor_name} added successfully!")

    st.markdown("<h1 style='text-align: center; color: white;'>Recruit Data</h1>", unsafe_allow_html=True)
    st.dataframe(data, hide_index=True)

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

  conn_thermomix = connect(
      database=config["DATABASE_NAME"]
  )

  live_df, calendar, team_leaders = get_data(conn_thermomix)

  conn_thermomix = connect(
      database=config["DATABASE_NAME"]
  )

  create_inserts(live_df, calendar, team_leaders, conn_thermomix)
