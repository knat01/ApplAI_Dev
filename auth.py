# auth.py

import streamlit as st
from firebase_admin import auth, firestore, initialize_app, credentials
import requests
import json
from urllib.parse import urlencode

import config

# Initialize Firebase Admin SDK if not already initialized
def initialize_firebase():
    if not firebase_admin._apps:
        try:
            config.set_firebase_project_id()  # Set the Project ID
            cred = credentials.Certificate(config.get_firebase_config())
            initialize_app(cred)
        except ValueError as e:
            st.error(f"Firebase initialization error: {str(e)}")
            return False
    return True

# Import firebase_admin after defining initialize_firebase to avoid NameError
import firebase_admin

if initialize_firebase():
    db = firestore.client()
else:
    st.error("Failed to initialize Firebase. Please check your configuration.")
    st.stop()

# Firebase REST API key
FIREBASE_API_KEY = config.get_firebase_api_key()

def login_signup():
    """
    Renders the Login and Sign-Up tabs with respective forms.
    """
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    # ----- Login Tab -----
    with tab1:
        st.subheader("Login")
        with st.form(key="login_form"):
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            submit_login = st.form_submit_button(label="Login")

        if submit_login:
            try:
                # Firebase Authentication via REST API
                login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
                payload = {
                    "email": login_email,
                    "password": login_password,
                    "returnSecureToken": True
                }
                response = requests.post(login_url, data=json.dumps(payload))
                result = response.json()

                if "error" in result:
                    st.error(result["error"]["message"])
                else:
                    # Verify ID Token and retrieve user information
                    user = auth.verify_id_token(result["idToken"])
                    st.session_state.user = {
                        "name": user.get("name") or user.get("email"),
                        "email": user.get("email"),
                        "uid": user.get("uid")
                    }
                    st.success("Logged in successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error logging in: {str(e)}")

    # ----- Sign-Up Tab -----
    with tab2:
        st.subheader("Sign Up")
        with st.form(key="signup_form"):
            signup_name = st.text_input("Name", key="signup_name")
            signup_email = st.text_input("Email", key="signup_email")
            signup_password = st.text_input("Password", type="password", key="signup_password")
            submit_signup = st.form_submit_button(label="Sign Up")

        if submit_signup:
            try:
                # Firebase Authentication via REST API
                signup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
                payload = {
                    "email": signup_email,
                    "password": signup_password,
                    "returnSecureToken": True
                }
                response = requests.post(signup_url, data=json.dumps(payload))
                result = response.json()

                if "error" in result:
                    st.error(result["error"]["message"])
                else:
                    # Update display name in Firebase Authentication
                    auth.update_user(
                        uid=result["localId"],
                        display_name=signup_name
                    )
                    st.success("Account created successfully! Please log in.")
            except Exception as e:
                st.error(f"Error creating account: {str(e)}")

    # ----- Google Sign-In -----
    st.markdown("---")
    st.subheader("Or")
    if st.button("Sign in with Google"):
        # Construct the OAuth URL
        redirect_uri = config.get_redirect_uri()  # Read from config.py
        google_oauth_credentials = config.get_google_oauth_credentials()
        params = {
            "client_id": google_oauth_credentials["client_id"],
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent"
        }
        oauth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        st.markdown(f"<a href='{oauth_url}' target='_self'>Click here to sign in with Google</a>", unsafe_allow_html=True)

def handle_google_signin():
    """
    Handles the OAuth redirect from Google, exchanges authorization code for tokens,
    verifies the ID token, and logs the user in by setting session state.
    """
    # Parse the URL to get the authorization code
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]
        # Exchange code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        redirect_uri = config.get_redirect_uri()
        google_oauth_credentials = config.get_google_oauth_credentials()
        payload = {
            "code": code,
            "client_id": google_oauth_credentials["client_id"],
            "client_secret": google_oauth_credentials["client_secret"],
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        response = requests.post(token_url, data=payload)
        tokens = response.json()

        if "error" in tokens:
            st.error(tokens["error"])
        else:
            id_token = tokens["id_token"]
            try:
                # Verify the ID token and get user info
                user = auth.verify_id_token(id_token)
                st.session_state.user = {
                    "name": user.get("name") or user.get("email"),
                    "email": user.get("email"),
                    "uid": user.get("uid")
                }
                st.success("Logged in with Google successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error verifying token: {str(e)}")

def logout():
    """
    Logs the user out by clearing the session state.
    """
    st.session_state.pop('user', None)
    st.success("Logged out successfully!")
    st.rerun()
