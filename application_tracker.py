import streamlit as st
from firebase_admin import firestore
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
        salary = st.number_input("Salary (if known)", min_value=0, step=1000, key="salary_input")

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
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame([doc.to_dict() for doc in applications])
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])

    # Display applications
    if not df.empty:
        st.subheader("Your Applications")
        st.dataframe(df)

        # Update or delete applications
        selected_app = st.selectbox("Select an application to update or delete:", df['company'] + " - " + df['position'])
        if selected_app:
            app_index = df.index[df['company'] + " - " + df['position'] == selected_app][0]
            app_id = applications[app_index].id
            
            new_status = st.selectbox("Update Status", ["Applied", "Interview Scheduled", "Offer Received", "Rejected"], key=f"update_status_{app_id}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update Status", key=f"update_button_{app_id}"):
                    applications_ref.document(app_id).update({'status': new_status})
                    st.success("Status updated successfully!")
                    st.experimental_rerun()
            
            with col2:
                if st.button("Delete Application", key=f"delete_button_{app_id}"):
                    applications_ref.document(app_id).delete()
                    st.success("Application deleted successfully!")
                    st.experimental_rerun()

    # Advanced Analytics
    st.subheader("Application Insights")

    if not df.empty:
        # 1. Application Status Distribution
        status_counts = df['status'].value_counts()
        fig_status = px.pie(values=status_counts.values, names=status_counts.index, title="Application Status Distribution")
        st.plotly_chart(fig_status)

        # 2. Application Trend Over Time
        df_sorted = df.sort_values('date')
        fig_trend = px.line(df_sorted, x='date', y=df_sorted.index, title="Application Submission Trend")
        st.plotly_chart(fig_trend)

        # 3. Top Companies Applied
        top_companies = df['company'].value_counts().head(10)
        fig_companies = px.bar(x=top_companies.index, y=top_companies.values, title="Top 10 Companies Applied")
        st.plotly_chart(fig_companies)

        # 4. Salary Distribution (for known salaries)
        df_salary = df[df['salary'] > 0]
        if not df_salary.empty:
            fig_salary = px.box(df_salary, y='salary', title="Salary Distribution")
            st.plotly_chart(fig_salary)

        # 5. Application Success Rate
        success_rate = (df['status'].isin(['Offer Received', 'Interview Scheduled']).sum() / len(df)) * 100
        st.metric("Application Success Rate", f"{success_rate:.2f}%")

        # 6. Recent Activity
        st.subheader("Recent Activity")
        recent_df = df[df['date'] >= (datetime.now() - timedelta(days=30))].sort_values('date', ascending=False)
        st.table(recent_df[['date', 'company', 'position', 'status']])

        # 7. Application Funnel
        funnel_data = df['status'].value_counts().sort_values(ascending=True)
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_data.index,
            x=funnel_data.values,
            textinfo="value+percent initial"
        ))
        fig_funnel.update_layout(title_text="Application Funnel")
        st.plotly_chart(fig_funnel)

        # 8. Time to Response Analysis
        df['response_time'] = (datetime.now() - df['date']).dt.days
        avg_response_time = df['response_time'].mean()
        st.metric("Average Response Time", f"{avg_response_time:.1f} days")

        # 9. Position Type Analysis
        position_types = df['position'].str.extract('(Developer|Engineer|Manager|Analyst|Designer)')
        position_type_counts = position_types[0].value_counts()
        fig_position_types = px.pie(values=position_type_counts.values, names=position_type_counts.index, title="Position Types Applied")
        st.plotly_chart(fig_position_types)

        # 10. Application Heatmap
        df['weekday'] = df['date'].dt.weekday
        df['week'] = df['date'].dt.isocalendar().week
        heatmap_data = df.groupby(['week', 'weekday']).size().unstack()
        fig_heatmap = px.imshow(heatmap_data, labels=dict(x="Day of Week", y="Week of Year", color="Applications"),
                                x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                                title="Application Submission Heatmap")
        st.plotly_chart(fig_heatmap)

    else:
        st.info("No applications added yet. Start by adding your job applications!")

    # Application Statistics
    st.subheader("Application Statistics")
    if not df.empty:
        total_applications = len(df)
        st.write(f"Total Applications: {total_applications}")

        status_counts = df['status'].value_counts()
        for status, count in status_counts.items():
            st.write(f"{status}: {count}")

        # Additional Statistics
        unique_companies = df['company'].nunique()
        st.write(f"Unique Companies Applied: {unique_companies}")

        if 'salary' in df.columns and df['salary'].sum() > 0:
            avg_salary = df[df['salary'] > 0]['salary'].mean()
            st.write(f"Average Salary (of known salaries): ${avg_salary:,.2f}")

        time_range = (df['date'].max() - df['date'].min()).days
        if time_range > 0:
            applications_per_day = total_applications / time_range
            st.write(f"Average Applications per Day: {applications_per_day:.2f}")

    else:
        st.write("No applications data available.")
