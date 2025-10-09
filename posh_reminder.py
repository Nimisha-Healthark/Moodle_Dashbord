import pandas as pd
from datetime import datetime
import numpy as np
from df_views import preprocess_df

def fetch_posh_df() -> pd.DataFrame:
    df = pd.read_excel(r'Documents\POSH_Reminder_data.xlsx', index_col=False)
    return df

def prepare_reminder_list(posh_df: pd.DataFrame) -> pd.DataFrame:
    current_date = datetime.now().date()
    posh_df['Date of Reminder'] = pd.to_datetime(posh_df['Date of Reminder']).dt.date
    reminder_df = posh_df[posh_df['Date of Reminder'] <= current_date]

    return reminder_df

def add_new_employee():
    original_df = pd.read_excel(r'Documents\Healthark Academy User Details.xlsx')
    original_df = preprocess_df(original_df)

    posh_df = pd.read_excel(r'Documents\POSH_Reminder_data.xlsx')

    # Identify missing names
    missing_rows = original_df.loc[
        ~original_df['User'].isin(posh_df['User']),
        ['User', 'Email', 'Time enrolled', 'Time completed']
    ].copy()

    if not missing_rows.all().all():
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

    updated_df.to_excel(r'Documents\POSH_Reminder_data.xlsx', index=False)

# only for the first time, after use add_new_employee
def create_fresh_report():
    original_df = pd.read_excel(r'Documents\Healthark Academy User Details.xlsx')
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
    
    posh_df = posh_df.drop(columns="index", errors='ignore')

    posh_df.to_excel(r'Documents\POSH_Reminder_data.xlsx', index=False)

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
    posh_df.to_excel(r'Documents\POSH_Reminder_data.xlsx', index=False)