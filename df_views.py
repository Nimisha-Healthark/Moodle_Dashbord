import pandas as pd
from typing import List
import streamlit as st

def preprocess_df(df: pd.DataFrame) -> pd.DataFrame:
    # # Remove unwanted rows
    # df = df[df['Full name with picture and link'] != "Healthark Insights"].reset_index(drop=True)

    # # Rename columns
    # df = df.rename(columns={
    #     'Full name with picture and link': 'User',
    #     'Course full name': 'Courses',
    #     'Student progress': 'Progress',
    #     'Email address': 'Email'
    # })

    # # Parse datetime and extract year/month
    # df['Time enrolled'] = pd.to_datetime(df['Time enrolled'])
    # df['Year'] = df['Time enrolled'].dt.year
    # df['Month'] = df['Time enrolled'].dt.month

    # return df
    """Preprocess Moodle user report DataFrame safely."""
    expected_col = "Full name with picture and link"

    # Log available columns for debugging
    available_cols = df.columns.tolist()
    #st.write("📊 Columns found in uploaded Excel:", available_cols)

    # If expected column missing, show warning and skip filtering
    if expected_col not in df.columns:
        st.warning(
            f"⚠️ Expected column '{expected_col}' not found. "
            f"Available columns are: {', '.join(available_cols)}"
        )
        # Try to rename any similar columns automatically
        rename_map = {}
        for col in df.columns:
            if "full name" in col.lower() and "link" in col.lower():
                rename_map[col] = "User"
            elif "course" in col.lower():
                rename_map[col] = "Courses"
            elif "progress" in col.lower():
                rename_map[col] = "Progress"
            elif "email" in col.lower():
                rename_map[col] = "Email"
        df = df.rename(columns=rename_map)
        return df.reset_index(drop=True)

    # Remove unwanted rows
    df = df[df[expected_col] != "Healthark Insights"].reset_index(drop=True)

    # Rename columns
    df = df.rename(columns={
        expected_col: 'User',
        'Course full name': 'Courses',
        'Student progress': 'Progress',
        'Email address': 'Email'
    })

    # Handle missing datetime safely
    if 'Time enrolled' in df.columns:
        df['Time enrolled'] = pd.to_datetime(df['Time enrolled'], errors='coerce')
        df['Year'] = df['Time enrolled'].dt.year
        df['Month'] = df['Time enrolled'].dt.month
    else:
        st.warning("⚠️ Column 'Time enrolled' not found in data.")
        df['Year'], df['Month'] = None, None

    return df


def course_view(df: pd.DataFrame, status: str, course: List[str]) -> pd.DataFrame:
    status_df = df[df['Status'] == status] if status != 'All' else df
    course_df = status_df[status_df['Courses'].isin(course)] if 'All' not in course else status_df
    return course_df

def threshold_view(df: pd.DataFrame, month: str, year: str, course: list[str], threshold: int) -> pd.DataFrame:
    df = df[df['Status'] != 'Not current'].reset_index(drop=True)

    # Ensure Progress column is numeric
    df['Progress'] = pd.to_numeric(df['Progress'], errors='coerce')

    year_df = df[df['Year'] == year] if year != 'All' else df
    month_df = year_df[year_df['Month'] == month] if month != 'All' else year_df
    view = month_df[month_df['Courses'].isin(course)] if 'All' not in course else month_df

    # Filter by progress threshold
    view = view[view['Progress'] < threshold]

    return view