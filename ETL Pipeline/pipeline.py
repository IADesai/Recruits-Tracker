"""Main code that runs the pipeline"""
from Transform.transform import *
from Load.load import *

if __name__ == "__main__":

    # Transform

    recruits_df_2023 = turn_2023_recruits_xls_to_dataframe()

    recruits_df_2024 = turn_2024_recruits_xls_to_dataframe()

    recruits_df_2023.to_csv("ExcelSheets/2023Recruits.csv", index=False)   
    
    recruits_df_2024.to_csv("ExcelSheets/2024Recruits.csv", index=False) 

    # Load

    # create_database()
    
    conn_thermomix = get_db_connection()
    
    create_tables(conn_thermomix)

    populate_database(conn_thermomix)