import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
from config import firebase_config
import auth as auth_module
import resume_parser
import ai_generator
import application_tracker
import payment

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def main():
    st.set_page_config(page_title="AI Job Application Assistant", page_icon="📄", layout="wide")
    st.title("AI Job Application Assistant")

    # Check if user is logged in
    if 'user' not in st.session_state:
        auth_module.login_signup()
    else:
        show_main_app()

def show_main_app():
    st.sidebar.title(f"Welcome, {st.session_state.user['name']}!")
    st.sidebar.button("Logout", on_click=auth_module.logout)

    menu = ["Upload Resume", "Generate Documents", "Application Tracker", "Upgrade Plan"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Upload Resume":
        resume_parser.upload_resume()
    elif choice == "Generate Documents":
        ai_generator.generate_documents()
    elif choice == "Application Tracker":
        application_tracker.show_tracker()
    elif choice == "Upgrade Plan":
        payment.show_upgrade_options()

if __name__ == "__main__":
    main()
