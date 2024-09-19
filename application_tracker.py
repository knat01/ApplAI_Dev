import streamlit as st
from firebase_admin import firestore
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')

db = firestore.client()

def show_tracker():
    st.subheader("Application Tracker")

    user_id = st.session_state.user['uid']
    applications_ref = db.collection('users').document(user_id).collection('applications')

    # Add new application (existing code)
    # ...

    # Fetch all applications
    applications = list(applications_ref.stream())
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame([doc.to_dict() for doc in applications])
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])

    # Display applications (existing code)
    # ...

    # Advanced Analytics
    st.subheader("Advanced Application Insights")

    if not df.empty:
        # Existing visualizations (Status Distribution, Trend, etc.)
        # ...

        # New Advanced Analytics
        
        # 1. Application Success Rate over time
        st.subheader("Application Success Rate Over Time")
        df['is_successful'] = df['status'].isin(['Offer Received', 'Interview Scheduled'])
        df_success = df.set_index('date').resample('W')['is_successful'].mean().reset_index()
        fig_success_rate = px.line(df_success, x='date', y='is_successful', title="Weekly Application Success Rate")
        st.plotly_chart(fig_success_rate)

        # 2. Average Response Time by Company
        st.subheader("Average Response Time by Company")
        df['response_time'] = (df['date'] - df['date'].min()).dt.days
        avg_response_time = df.groupby('company')['response_time'].mean().sort_values(ascending=False)
        fig_response_time = px.bar(avg_response_time, title="Average Response Time by Company (Days)")
        st.plotly_chart(fig_response_time)

        # 3. Job Application Seasonality Analysis
        st.subheader("Job Application Seasonality")
        df['month'] = df['date'].dt.month
        monthly_apps = df['month'].value_counts().sort_index()
        fig_seasonality = px.bar(x=monthly_apps.index.map(lambda x: calendar.month_abbr[x]), 
                                 y=monthly_apps.values, 
                                 title="Job Applications by Month",
                                 labels={'x': 'Month', 'y': 'Number of Applications'})
        st.plotly_chart(fig_seasonality)

        # 4. Skills Gap Analysis
        st.subheader("Skills Gap Analysis")
        all_skills = ' '.join(df['position'].tolist())
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(all_skills.lower())
        filtered_skills = [word for word in word_tokens if word.isalnum() and word not in stop_words]
        skills_freq = Counter(filtered_skills).most_common(10)
        fig_skills = px.bar(x=[skill[0] for skill in skills_freq], 
                            y=[skill[1] for skill in skills_freq],
                            title="Top 10 Skills in Job Listings",
                            labels={'x': 'Skill', 'y': 'Frequency'})
        st.plotly_chart(fig_skills)

        # 5. Geographical Distribution of Applications
        st.subheader("Geographical Distribution of Applications")
        location_counts = df['location'].value_counts()
        fig_geo = px.pie(values=location_counts.values, names=location_counts.index, title="Application Distribution by Location")
        st.plotly_chart(fig_geo)

    else:
        st.info("No applications added yet. Start by adding your job applications!")

    # Application Statistics (existing code)
    # ...

