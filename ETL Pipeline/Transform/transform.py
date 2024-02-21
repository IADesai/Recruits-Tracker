"""This module contains functions used to transform the data into the appropriate output form."""
import pandas as pd
import os


def turn_2023_recruits_xls_to_dataframe() -> pd.DataFrame:
    """Finds the file and turns it into a pandas dataframe"""
    source = os.path.abspath('ExcelSheets/')
    files = [file for file in os.listdir(source) if ".xlsx" in file]
    df = pd.read_excel(f"ExcelSheets/{files[0]}", index_col=False, sheet_name='Recruits Tracker 2223')
    df.columns = df.columns.str.strip()
    return df


def turn_2024_recruits_xls_to_dataframe() -> pd.DataFrame:
    """Finds the file and turns it into a pandas dataframe"""
    source = os.path.abspath('ExcelSheets/')
    files = [file for file in os.listdir(source) if ".xlsx" in file]
    df = pd.read_excel(f"ExcelSheets/{files[0]}", index_col=False, sheet_name='Recruits Tracker24')
    df.columns = df.columns.str.strip()
    return df


if __name__ == "__main__":
    recruits_df_2023 = turn_2023_recruits_xls_to_dataframe()
    recruits_df_2024 = turn_2024_recruits_xls_to_dataframe()
