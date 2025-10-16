import streamlit as st
import pandas as pd
from mail_excel import fetch_excel_attachment, load_report
from df_views import preprocess_df, course_view, threshold_view
from mailSending import send_bulk_emails, send_POSH_emails
from json import load
from posh_reminder import add_new_employee, fetch_posh_df, prepare_reminder_list, set_new_reminder

@st.dialog("Sending a Nudge")
def nudge(df: pd.DataFrame, email_send):
    if not st.session_state.get("nudge", False):
        return  # Early exit if not in nudge mode

    years = ['All'] + sorted(df['Year'].dropna().unique().tolist())
    selected_year = st.selectbox("Select Target Year of Enrollment", years)

    months = ['All'] + sorted(df['Month'].dropna().unique().tolist())
    selected_month = st.selectbox("Select Target Month of Enrollment", months)

    courses = ['All'] + sorted(df['Courses'].dropna().unique().tolist())
    selected_courses = st.multiselect("Select Target Course(s)", courses, default=['All'])

    threshold = st.select_slider(
        "Select the Minimum Threshold Value",
        options=list(range(0, 110, 10))
    )

    # Apply filters based on selection
    filtered = df.copy()
    if selected_year != 'All':
        filtered = filtered[filtered['Year'] == selected_year]
    if selected_month != 'All':
        filtered = filtered[filtered['Month'] == selected_month]
    if 'All' not in selected_courses:
        filtered = filtered[filtered['Courses'].isin(selected_courses)]

    filtered = filtered[filtered['Progress'] <= threshold]

    st.write("Preview of selected users to nudge:")
    st.dataframe(filtered[['User', 'Email', 'Courses', 'Progress']])

    if st.button("Confirm and Send Nudge Emails"):
        # TEST_ADDRESS = "devadyumna@healtharkinsights.com"
        payloads = []

        # Group by email and user, aggregate incomplete courses
        grouped = (
            filtered[filtered['Email'].str.lower()] #== TEST_ADDRESS
            .groupby(['Email', 'User'])['Courses']
            .apply(list)
            .reset_index()
        )

        for _, row in grouped.iterrows():
            payloads.append((row['Email'], row['User'], row['Courses']))

        if not payloads:
            st.info("No test emails to send.")
        else:
            failed = send_bulk_emails(email_send, payloads)
            if failed:
                st.error(f"Failed to send email to: {', '.join(failed)}")
            else:
                st.success("Nudges sent successfully.")
        st.rerun()

    if st.button("Close"):
        st.rerun()

def app(df: pd.DataFrame):
    # with cont_col1:
    st.header("Enrolled Users in Course")

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            # course selection applicable throughout
            courses = df['Courses'].unique().tolist()
            courses.insert(0, 'All')
            selected_course = st.multiselect(label='Select Course', options=courses)

        with col2:
            # status selection
            status = df['Status'].unique().tolist()
            status.insert(0, 'All')
            selected_status = st.selectbox(label='Enter Status of Student', options=status)

    enrolled_users = course_view(df, selected_status, selected_course)
    st.dataframe(enrolled_users, use_container_width=True)

    # with cont_col2:
    st.header("Users Below Threshold Progress in the Selected Course:")

    with st.container():
        cols= st.columns(3)
        
        with cols[0]:
            # selection of year
            years = df['Year'].unique().tolist()
            years.insert(0, 'All')
            selected_year = st.selectbox(label='Select Year of Enrollment', options=years)
        
        with cols[1]:
            # selection of month
            months = df['Month'].unique().tolist()
            months.insert(0, 'All')
            selected_month = st.selectbox(label='Select Month of Enrollment', options=months)
        
        with cols[2]:
            # user input taken for threshold (jic)
            threshold = st.select_slider(
                "Select the Threshold Value",
                options = list(range(0, 110, 10))
            )

    st.dataframe(threshold_view(df, selected_month, selected_year, selected_course, threshold), use_container_width=True)

@st.dialog("POSH Early Reminder")
def posh_reminder(sender_email):
    if not st.session_state.get("posh", False):
        return  # Early exit if not in posh mode

    posh_df = fetch_posh_df()
    reminder_df = prepare_reminder_list(posh_df)

    if not reminder_df.empty:
        st.dataframe(reminder_df)

        grouped = (
            reminder_df
            .groupby(['Email', 'User'])['Date of Reminder']
            .apply(list)
            .reset_index()
        )

        payloads = [(row['User'], row['Email']) for _, row in grouped.iterrows()]

        if not payloads:
            st.info("No Emails to Send")
        else:
            failed = send_POSH_emails(sender_email, payloads)
            if failed:
                st.error(f"Failed to send email to: {', '.join(failed)}")
            else:
                st.success("Nudges sent successfully.")

        set_new_reminder(reminder_df, posh_df)
    else:
        st.info("No records to show or send.")

    if st.button("Close"):
        st.rerun()

if __name__ == "__main__":
    try:
        email_use = st.secrets["gmail_sender"]["email"]
    except Exception as e:
        st.error(f"Error: {str(e)}")
            
    excel_filepath = fetch_excel_attachment()  # ✅ new Gmail API function type:ignore
    # excel_filepath = r"downloads\Healthark Academy Testing Users Details.xlsx"

    try:
        add_new_employee()
        st.set_page_config(layout='wide')
        st.session_state.nudge = False
        st.session_state.posh = False
        df = load_report(excel_filepath) #type: ignore
        df = preprocess_df(df)

        st.markdown("<h1 style='text-align: center;'>Moodle Dashboard</h1>", unsafe_allow_html=True)

        with st.container():
            app(df)

        if st.button("Nudge Users Below Threshold"):
            st.session_state.nudge = True

        if st.session_state.nudge:
            nudge(df, email_use) #type: ignore
        
        if st.button("Send POSH Reminder"):
            st.session_state.posh = True
        
        if st.session_state.posh:
            posh_reminder(email_use) #type: ignore

    except Exception as e:
        st.error(f"Error: {str(e)}")