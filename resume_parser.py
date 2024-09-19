import streamlit as st
from pdfminer.high_level import extract_text
from docx import Document
import re
import firebase_admin
from firebase_admin import credentials, firestore
from config import get_firebase_config

# Initialize Firebase
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(get_firebase_config())
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    st.error(f"Error initializing Firebase: {str(e)}")
    db = None

def extract_text_from_pdf(file):
    return extract_text(file)

def extract_text_from_docx(file):
    doc = Document(file)
    return " ".join([paragraph.text for paragraph in doc.paragraphs])

def parse_resume(text):
    # Basic parsing logic - can be extended for more sophisticated parsing
    name = re.search(r'^([A-Z][a-z]+ [A-Z][a-z]+)', text, re.MULTILINE)
    email = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    phone = re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
    
    skills = re.findall(r'(?:Skills|SKILLS)(?:[\s\S]*?)(?:\n\n|\Z)', text)
    skills = [skill.strip() for skill in skills[0].split('\n') if skill.strip()] if skills else []
    
    experience = re.findall(r'(?:Experience|EXPERIENCE)(?:[\s\S]*?)(?:\n\n|\Z)', text)
    experience = experience[0] if experience else ""

    return {
        "name": name.group(1) if name else "",
        "email": email.group(0) if email else "",
        "phone": phone.group(0) if phone else "",
        "skills": skills,
        "experience": experience
    }

def upload_resume():
    st.subheader("Upload Your Resume")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])
    
    if uploaded_file is not None:
        file_type = uploaded_file.type
        if file_type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = extract_text_from_docx(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload a PDF or DOCX file.")
            return

        parsed_data = parse_resume(text)
        
        st.subheader("Parsed Resume Data")
        st.write(parsed_data)
        
        if st.button("Save Resume Data"):
            if db is not None:
                user_id = st.session_state.user['uid']
                db.collection('users').document(user_id).set({
                    'resume_data': parsed_data
                }, merge=True)
                st.success("Resume data saved successfully!")
            else:
                st.error("Unable to save resume data due to database connection issues.")
