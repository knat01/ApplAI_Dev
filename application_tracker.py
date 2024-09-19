import streamlit as st
from firebase_admin import firestore
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

db = firestore.client()

def show_tracker():
    st.subheader("Application Tracker")

    user_id = st.session_state.user['uid']
    applications_ref = db.collection('users').document(user_id).collection('applications')

    # Add new application
    with st.expander("Add New Application"):
        company = st.text_input("Company Name", key="company_name_input")
        position = st.text_input("Position", key="position_input")
        status = st.selectbox(
            "Status",
            ["Applied", "Interview Scheduled", "Offer Received", "Rejected"],
            key="status_select")
        date = st.date_input("Application Date", key="application_date_input")
        salary = st.number_input("Salary (if available)", min_value=0, step=1000, key="salary_input")

        if st.button("Add Application", key="add_application_button"):
            applications_ref.add({
                'company': company,
                'position': position,
                'status': status,
                'date': date.isoformat(),
                'salary': salary
            })
            st.success("Application added successfully!")

    # Fetch all applications
    applications = list(applications_ref.stream())
    
    if not applications:
        st.info("No applications found. Start adding your job applications!")
        return

    # Convert to DataFrame for easier analysis
    df = pd.DataFrame([doc.to_dict() for doc in applications])
    df['date'] = pd.to_datetime(df['date'])

    # Display applications
    st.subheader("Your Applications")
    st.dataframe(df)

    # Advanced Analytics
    st.subheader("Application Insights")

    # 1. Application Status Distribution
    status_counts = df['status'].value_counts()
    fig_status = px.pie(status_counts, values=status_counts.values, names=status_counts.index, title="Application Status Distribution")
    st.plotly_chart(fig_status)

    # 2. Application Timeline
    fig_timeline = px.timeline(df, x_start="date", y="company", color="status", title="Application Timeline")
    st.plotly_chart(fig_timeline)

    # 3. Salary Distribution (for offers received)
    offers = df[df['status'] == 'Offer Received']
    if not offers.empty:
        fig_salary = px.box(offers, y="salary", title="Salary Distribution for Offers Received")
        st.plotly_chart(fig_salary)

    # 4. Application Frequency
    df['week'] = df['date'].dt.to_period('W')
    weekly_counts = df.groupby('week').size().reset_index(name='count')
    weekly_counts['week'] = weekly_counts['week'].astype(str)
    fig_frequency = px.line(weekly_counts, x='week', y='count', title="Weekly Application Frequency")
    st.plotly_chart(fig_frequency)

    # 5. Success Rate
    success_rate = (df['status'] == 'Offer Received').mean() * 100
    st.metric("Overall Success Rate", f"{success_rate:.2f}%")

    # 6. Time to Interview
    df_interviewed = df[df['status'].isin(['Interview Scheduled', 'Offer Received', 'Rejected'])]
    if not df_interviewed.empty:
        avg_time_to_interview = (df_interviewed['date'] - df['date'].min()).mean().days
        st.metric("Average Time to Interview", f"{avg_time_to_interview:.1f} days")

    # 7. Most Applied Positions
    top_positions = df['position'].value_counts().head(5)
    st.subheader("Top 5 Positions Applied")
    st.bar_chart(top_positions)

    # 8. Application Forecast
    last_30_days = datetime.now() - timedelta(days=30)
    recent_apps = df[df['date'] > last_30_days]
    if not recent_apps.empty:
        daily_app_rate = len(recent_apps) / 30
        forecast_30_days = int(daily_app_rate * 30)
        st.metric("Forecasted Applications (Next 30 Days)", forecast_30_days)

    # Allow updating application status
    st.subheader("Update Application Status")
    selected_app = st.selectbox("Select Application to Update", df['company'] + " - " + df['position'])
    new_status = st.selectbox("New Status", ["Applied", "Interview Scheduled", "Offer Received", "Rejected"])
    if st.button("Update Status"):
        selected_doc = [doc for doc in applications if f"{doc.to_dict()['company']} - {doc.to_dict()['position']}" == selected_app][0]
        selected_doc.reference.update({'status': new_status})
        st.success("Status updated successfully!")
        st.experimental_rerun()

def main():
    show_tracker()

if __name__ == "__main__":
    main()
