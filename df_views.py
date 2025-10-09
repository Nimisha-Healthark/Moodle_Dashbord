import pandas as pd
from typing import List

def preprocess_df(df: pd.DataFrame) -> pd.DataFrame:
    # Remove unwanted rows
    df = df[df['Full name with picture and link'] != "Healthark Insights"].reset_index(drop=True)

    # Rename columns
    df = df.rename(columns={
        'Full name with picture and link': 'User',
        'Course full name': 'Courses',
        'Student progress': 'Progress',
        'Email address': 'Email'
    })

    # Parse datetime and extract year/month
    df['Time enrolled'] = pd.to_datetime(df['Time enrolled'])
    df['Year'] = df['Time enrolled'].dt.year
    df['Month'] = df['Time enrolled'].dt.month

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