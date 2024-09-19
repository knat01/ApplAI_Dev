import streamlit as st
from firebase_admin import auth

def login_signup():
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            try:
                user = auth.get_user_by_email(email)
                # In a real-world scenario, you would verify the password here
                st.session_state.user = {
                    "name": user.display_name or user.email,
                    "email": user.email,
                    "uid": user.uid
                }
                st.success("Logged in successfully!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error logging in: {str(e)}")

    with tab2:
        st.subheader("Sign Up")
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Sign Up"):
            try:
                user = auth.create_user(
                    email=email,
                    password=password,
                    display_name=name
                )
                st.success("Account created successfully! Please log in.")
            except Exception as e:
                st.error(f"Error creating account: {str(e)}")

def logout():
    st.session_state.pop('user', None)
    st.success("Logged out successfully!")
    st.experimental_rerun()
