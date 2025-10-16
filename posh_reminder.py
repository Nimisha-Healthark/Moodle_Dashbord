import pandas as pd
from datetime import datetime
import numpy as np
from df_views import preprocess_df
import gspread
from google.oauth2.service_account import Credentials

# =========================
# Google Sheets Integration
# =========================

def get_gsheet_client():
    """Authenticate and return gspread client using service account JSON in Streamlit secrets."""
    creds_json = st.secrets["google_sheets"]["credentials"]
    creds_dict = eval(creds_json) if isinstance(creds_json, str) else creds_json

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(credentials)


def read_sheet(sheet_name: str) -> pd.DataFrame:
    """Read a sheet as a pandas DataFrame."""
    client = get_gsheet_client()
    sheet = client.open(sheet_name).sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)


def write_sheet(sheet_name: str, df: pd.DataFrame):
    """Write a pandas DataFrame back to Google Sheets."""
    client = get_gsheet_client()
    sheet = client.open(sheet_name).sheet1
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

# =================================================
# POSH Reminder Specific Functions
# =================================================

SHEET_POSH = "POSH_Reminder_data"
SHEET_USERS = "Healthark_Academy_User_Details"

def fetch_posh_df() -> pd.DataFrame:
    df = df = read_sheet(SHEET_POSH)
    return df

def prepare_reminder_list(posh_df: pd.DataFrame) -> pd.DataFrame:
    current_date = datetime.now().date()
    posh_df['Date of Reminder'] = pd.to_datetime(posh_df['Date of Reminder']).dt.date
    reminder_df = posh_df[posh_df['Date of Reminder'] <= current_date]
    return reminder_df

def add_new_employee():
    original_df = read_sheet(SHEET_USERS)
    original_df = preprocess_df(original_df)
    posh_df = read_sheet(SHEET_POSH)

    # Identify missing names
    missing_rows = original_df.loc[
        ~original_df['User'].isin(posh_df['User']),
        ['User', 'Email', 'Time enrolled', 'Time completed']
    ].copy()

    if missing_rows.empty:
        return

    # Rename to match posh_df's column names
    missing_rows.rename(
        columns={
            'Time enrolled': 'Date Started',
            'Time completed': 'Date Ended'
        }, 
        inplace=True
    )

    missing_rows['Date Started'] = pd.to_datetime(missing_rows['Date Started']).dt.date
    missing_rows['Date Ended'] = pd.to_datetime(missing_rows['Date Ended']).dt.date

    missing_rows['Date of Reminder'] = np.where(
        missing_rows['Date Ended'].notna(),
        missing_rows['Date Ended'] + pd.DateOffset(years=1),
        missing_rows['Date Started'] + pd.DateOffset(years=1)
    )

    missing_rows['Date of Reminder'] = pd.to_datetime(missing_rows['Date of Reminder']).dt.date

    # Append missing rows to posh_df
    updated_df = pd.concat([posh_df, missing_rows], ignore_index=True )

    write_sheet(SHEET_POSH, updated_df)

# only for the first time, after use add_new_employee
def create_fresh_report():
    original_df = read_sheet(SHEET_USERS)
    original_df = preprocess_df(original_df)
    df = original_df[original_df['Courses'].str.lower() == 'prevention of sexual harassment']
    df.drop_duplicates(inplace=True)

    posh_df = pd.DataFrame()

    posh_df['User'] = df['User']
    posh_df['Email'] = df['Email']
    posh_df['Date Started'] = pd.to_datetime(df['Time enrolled']).dt.date
    posh_df['Date Ended'] = pd.to_datetime(df['Time completed']).dt.date
    posh_df.reset_index(drop=True, inplace=True)
    posh_df['Date of Reminder'] = np.where(
            posh_df['Date Ended'].notna(),
            posh_df['Date Ended'] + pd.DateOffset(years=1),
            posh_df['Date Started'] + pd.DateOffset(years=1)
        )

    posh_df['Date of Reminder'] = pd.to_datetime(posh_df['Date of Reminder']).dt.date
    
    #posh_df = posh_df.drop(columns="index", errors='ignore')

    write_sheet(SHEET_POSH, posh_df)

def set_new_reminder(reminder_df: pd.DataFrame, posh_df: pd.DataFrame):
    # Make sure dates are datetime objects
    posh_df['Date Started'] = pd.to_datetime(posh_df['Date Started'])
    posh_df['Date of Reminder'] = pd.to_datetime(posh_df['Date of Reminder'])
    reminder_df['Date of Reminder'] = pd.to_datetime(reminder_df['Date of Reminder'])

    # Update only the subset due today
    for _, row in reminder_df.iterrows():
        user = row['User']
        new_start = row['Date of Reminder']              # today’s reminder date
        new_reminder = new_start + pd.DateOffset(years=1) # next year’s reminder

        posh_df.loc[posh_df['User'] == user, 'Date Started'] = new_start
        posh_df.loc[posh_df['User'] == user, 'Date of Reminder'] = new_reminder

    # Save the updated schedule
    write_sheet(SHEET_POSH, posh_df)