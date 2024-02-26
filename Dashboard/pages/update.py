"""Streamlit dashboard application code"""
from psycopg2 import connect
from psycopg2.extensions import connection
import streamlit as st
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

    st.markdown("<h1 style='text-align: center; color: white;'>Update Sales Information</h1>", unsafe_allow_html=True)


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


def handle_dnq(dnq_date, dnq_checkbox):
    return dnq_date if not dnq_checkbox else 'DNQ'


def create_sales_insert_form(data: pd.DataFrame, conn_insert: connection) -> None:
    """Creates the form for inserting sales information for a recruit"""

    with st.form("insert_sales_form"):
        form_column, data_column = st.columns(2)
        with form_column:
            unique_member_names = data['member_name'].unique()
            selected_recruit = st.selectbox('Select Recruit Name', unique_member_names)

            newcomer_demo_date = st.date_input("Newcomer Demo Date", key="newcomer_demo_date")

            st.markdown("Leave date fields empty if you do not want to add a date")

            # Sale 1
            date_column, dnq_column = st.columns(2)
            with date_column:
                first_sale_date = st.date_input("First Sale Date", key="first_sale_date", value=None)
            with dnq_column:
                st.markdown("")
                st.markdown("")
                first_sale_dnq = st.checkbox("First Sale DNQ")

            # Sale 2
            date_column, dnq_column = st.columns(2)
            with date_column:
                second_sale_date = st.date_input("Second Sale Date", key="second_sale_date", value=None)
            with dnq_column:
                st.markdown("")
                st.markdown("")
                second_sale_dnq = st.checkbox("Second Sale DNQ")

            # Sale 3
            date_column, dnq_column = st.columns(2)
            with date_column:
                third_sale_date = st.date_input("Third Sale Date", key="third_sale_date", value=None)
            with dnq_column:
                st.markdown("")
                st.markdown("")
                third_sale_dnq = st.checkbox("Third Sale DNQ")

            # Sale 4
            date_column, dnq_column = st.columns(2)
            with date_column:
                fourth_sale_date = st.date_input("Fourth Sale Date", key="fourth_sale_date", value=None)
            with dnq_column:
                st.markdown("")
                st.markdown("")
                fourth_sale_dnq = st.checkbox("Fourth Sale DNQ")

            # Sale 5
            date_column, dnq_column = st.columns(2)
            with date_column:
                fifth_sale_date = st.date_input("Fifth Sale Date", key="fifth_sale_date", value=None)
            with dnq_column:
                st.markdown("")
                st.markdown("")
                fifth_sale_dnq = st.checkbox("Fifth Sale DNQ")

            # Sale 6
            date_column, dnq_column = st.columns(2)
            with date_column:
                sixth_sale_date = st.date_input("Sixth Sale Date", key="sixth_sale_date", value=None)
            with dnq_column:
                st.markdown("")
                st.markdown("")
                sixth_sale_dnq = st.checkbox("Sixth Sale DNQ")

            # Sale 7
            date_column, dnq_column = st.columns(2)
            with date_column:
                seventh_sale_date = st.date_input("Seventh Sale Date", key="seventh_sale_date", value=None)
            with dnq_column:
                st.markdown("")
                st.markdown("")
                seventh_sale_dnq = st.checkbox("Seventh Sale DNQ")

            # Sale 8
            date_column, dnq_column = st.columns(2)
            with date_column:
                eighth_sale_date = st.date_input("Eighth Sale Date", key="eighth_sale_date", value=None)
            with dnq_column:
                st.markdown("")
                st.markdown("")
                eighth_sale_dnq = st.checkbox("Eighth Sale DNQ")

            submit_sales = st.form_submit_button("Insert Sales Information")

        if submit_sales:
            cursor = conn_insert.cursor()
            cursor.execute("SELECT member_id FROM members WHERE name = %s", (selected_recruit,))
            member_id_fk_sales = cursor.fetchone()[0]

            # Check if the member already has a record in member_sales
            cursor.execute("SELECT * FROM member_sales WHERE member_id_fk = %s", (member_id_fk_sales,))
            existing_record = cursor.fetchone()

            if existing_record:
                # Member has an existing record, perform UPDATE
                cursor.execute("UPDATE member_sales SET "
                            "newcomer_demo = %s, "
                            "first_sale = %s, "
                            "second_sale = %s, "
                            "third_sale = %s, "
                            "fourth_sale = %s, "
                            "fifth_sale = %s, "
                            "sixth_sale = %s, "
                            "seventh_sale = %s, "
                            "eighth_sale = %s "
                            "WHERE member_id_fk = %s",
                            (newcomer_demo_date,
                                handle_dnq(first_sale_date, first_sale_dnq),
                                handle_dnq(second_sale_date, second_sale_dnq),
                                handle_dnq(third_sale_date, third_sale_dnq),
                                handle_dnq(fourth_sale_date, fourth_sale_dnq),
                                handle_dnq(fifth_sale_date, fifth_sale_dnq),
                                handle_dnq(sixth_sale_date, sixth_sale_dnq),
                                handle_dnq(seventh_sale_date, seventh_sale_dnq),
                                handle_dnq(eighth_sale_date, eighth_sale_dnq),
                                member_id_fk_sales))
            else:
                # Member doesn't have a record, perform INSERT
                cursor.execute("INSERT INTO member_sales (member_id_fk, newcomer_demo, first_sale, second_sale, third_sale, fourth_sale, fifth_sale, sixth_sale, seventh_sale, eighth_sale) "
                            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (member_id_fk_sales,
                                newcomer_demo_date,
                                handle_dnq(first_sale_date, first_sale_dnq),
                                handle_dnq(second_sale_date, second_sale_dnq),
                                handle_dnq(third_sale_date, third_sale_dnq),
                                handle_dnq(fourth_sale_date, fourth_sale_dnq),
                                handle_dnq(fifth_sale_date, fifth_sale_dnq),
                                handle_dnq(sixth_sale_date, sixth_sale_dnq),
                                handle_dnq(seventh_sale_date, seventh_sale_dnq),
                                handle_dnq(eighth_sale_date, eighth_sale_dnq)))

            conn_insert.commit()
            cursor.close()
            data, not_needed, not_needed_two = get_data(conn_insert)
            st.success(f"Sales information for recruit {selected_recruit} inserted successfully!")

        with data_column:
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

    create_sales_insert_form(live_df, conn_thermomix)
