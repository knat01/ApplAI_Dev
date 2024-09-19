# application_tracker.py

import streamlit as st
from firebase_admin import firestore

db = firestore.client()


def show_tracker():
    st.subheader("Application Tracker")

    user_id = st.session_state.user['uid']
    applications_ref = db.collection('users').document(user_id).collection(
        'applications')

    # Add new application
    with st.expander("Add New Application"):
        company = st.text_input("Company Name", key="company_name_input")
        position = st.text_input("Position", key="position_input")
        status = st.selectbox(
            "Status",
            ["Applied", "Interview Scheduled", "Offer Received", "Rejected"],
            key="status_select")
        date = st.date_input("Application Date", key="application_date_input")

        if st.button("Add Application", key="add_application_button"):
            applications_ref.add({
                'company': company,
                'position': position,
                'status': status,
                'date': date.isoformat()
            })
            st.success("Application added successfully!")

    # Display applications
    applications = applications_ref.stream()

    for app in applications:
        app_data = app.to_dict()
        with st.expander(f"{app_data['company']} - {app_data['position']}"):
            st.write(f"Status: {app_data['status']}")
            st.write(f"Date Applied: {app_data['date']}")

            # Update status
            new_status = st.selectbox("Update Status", [
                "Applied", "Interview Scheduled", "Offer Received", "Rejected"
            ],
                                      key=f"update_status_{app.id}")
            if new_status != app_data['status']:
                if st.button("Update Status", key=f"update_button_{app.id}"):
                    app.reference.update({'status': new_status})
                    st.success("Status updated successfully!")
                    st.experimental_rerun()

            # Delete application
            if st.button("Delete Application", key=f"delete_button_{app.id}"):
                app.reference.delete()
                st.success("Application deleted successfully!")
                st.experimental_rerun()

    # Display application statistics
    st.subheader("Application Statistics")
    total_applications = applications_ref.count().get()[0][0].value
    st.write(f"Total Applications: {total_applications}")

    status_counts = {}
    for app in applications_ref.stream():
        status = app.to_dict()['status']
        status_counts[status] = status_counts.get(status, 0) + 1

    for status, count in status_counts.items():
        st.write(f"{status}: {count}")
