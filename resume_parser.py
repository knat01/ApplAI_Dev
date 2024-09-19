# resume_parser.py

import streamlit as st
from firebase_admin import firestore
import firebase_admin
from firebase_admin import credentials
from pdfminer.high_level import extract_text
from docx import Document
import yaml
from openai import OpenAI
import config
import os

# Initialize Firebase if not already initialized
def initialize_firebase():
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(config.get_firebase_config())
            firebase_admin.initialize_app(cred)
        except ValueError:
            pass  # App already initialized

initialize_firebase()
db = firestore.client()

# Initialize OpenAI client
client = OpenAI(api_key=config.get_openai_api_key())

def extract_text_from_pdf(file):
    """
    Extracts text from a PDF file using pdfminer.

    Args:
        file (BytesIO): The uploaded PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    try:
        text = extract_text(file)
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def extract_text_from_docx(file):
    """
    Extracts text from a DOCX file using python-docx.

    Args:
        file (BytesIO): The uploaded DOCX file.

    Returns:
        str: Extracted text from the DOCX.
    """
    try:
        doc = Document(file)
        full_text = "\n".join([para.text for para in doc.paragraphs])
        return full_text
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {str(e)}")
        return ""

def parse_resume_with_openai(text):
    """
    Parses resume text into the specified YAML structure using OpenAI's API.

    Args:
        text (str): The extracted text from the resume.

    Returns:
        dict: Parsed resume data structured as per the YAML template.
    """
    prompt = f"""
    You are an AI assistant that extracts information from resumes and structures it into a predefined YAML format. Below is the extracted text from a resume. Please fill in the YAML template accurately based on the information provided.

    Extracted Resume Text:
    \"\"\"
    {text}
    \"\"\"

    YAML Template:
    ```yaml
    personal_information:
      name: "[Your Name]"
      surname: "[Your Surname]"
      date_of_birth: "[Your Date of Birth]"
      country: "[Your Country]"
      city: "[Your City]"
      address: "[Your Address]"
      phone_prefix: "[Your Phone Prefix]"
      phone: "[Your Phone Number]"
      email: "[Your Email Address]"
      github: "[Your GitHub Profile URL]"
      linkedin: "[Your LinkedIn Profile URL]"

    education_details:
      - education_level: "[Your Education Level]"
        institution: "[Your Institution]"
        field_of_study: "[Your Field of Study]"
        final_evaluation_grade: "[Your Final Evaluation Grade]"
        start_date: "[Start Date]"
        year_of_completion: "[Year of Completion]"
        exam:
          exam_name_1: "[Grade]"
          exam_name_2: "[Grade]"
          exam_name_3: "[Grade]"
          exam_name_4: "[Grade]"
          exam_name_5: "[Grade]"
          exam_name_6: "[Grade]"

    experience_details:
      - position: "[Your Position]"
        company: "[Company Name]"
        employment_period: "[Employment Period]"
        location: "[Location]"
        industry: "[Industry]"
        key_responsibilities:
          - responsibility_1: "[Responsibility Description]"
          - responsibility_2: "[Responsibility Description]"
          - responsibility_3: "[Responsibility Description]"
        skills_acquired:
          - "[Skill]"
          - "[Skill]"
          - "[Skill]"

      - position: "[Your Position]"
        company: "[Company Name]"
        employment_period: "[Employment Period]"
        location: "[Location]"
        industry: "[Industry]"
        key_responsibilities:
          - responsibility_1: "[Responsibility Description]"
          - responsibility_2: "[Responsibility Description]"
          - responsibility_3: "[Responsibility Description]"
        skills_acquired:
          - "[Skill]"
          - "[Skill]"
          - "[Skill]"

    projects:
      - name: "[Project Name]"
        description: "[Project Description]"
        link: "[Project Link]"

      - name: "[Project Name]"
        description: "[Project Description]"
        link: "[Project Link]"

    achievements:
      - name: "[Achievement Name]"
        description: "[Achievement Description]"
      - name: "[Achievement Name]"
        description: "[Achievement Description]"

    certifications:
      - name: "[Certification Name]"
        description: "[Certification Description]"
      - name: "[Certification Name]"
        description: "[Certification Description]"

    languages:
      - language: "[Language]"
        proficiency: "[Proficiency Level]"
      - language: "[Language]"
        proficiency: "[Proficiency Level]"

    interests:
      - "[Interest]"
      - "[Interest]"
      - "[Interest]"

    availability:
      notice_period: "[Notice Period]"

    salary_expectations:
      salary_range_usd: "[Salary Range]"

    self_identification:
      gender: "[Gender]"
      pronouns: "[Pronouns]"
      veteran: "[Yes/No]"
      disability: "[Yes/No]"
      ethnicity: "[Ethnicity]"

    legal_authorization:
      eu_work_authorization: "[Yes/No]"
      us_work_authorization: "[Yes/No]"
      requires_us_visa: "[Yes/No]"
      requires_us_sponsorship: "[Yes/No]"
      requires_eu_visa: "[Yes/No]"
      legally_allowed_to_work_in_eu: "[Yes/No]"
      legally_allowed_to_work_in_us: "[Yes/No]"
      requires_eu_sponsorship: "[Yes/No]"

    work_preferences:
      remote_work: "[Yes/No]"
      in_person_work: "[Yes/No]"
      open_to_relocation: "[Yes/No]"
      willing_to_complete_assessments: "[Yes/No]"
      willing_to_undergo_drug_tests: "[Yes/No]"
      willing_to_undergo_background_checks: "[Yes/No]"
    ```

    Please ensure that the YAML syntax is correct. If certain fields are not present in the resume text, leave them as empty strings or omit them.

    Output the YAML only without any additional text.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that structures resume information into YAML format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=1500
        )

        yaml_output = response.choices[0].message.content
        # Remove YAML markers if present
        yaml_output = yaml_output.replace("```yaml", "").replace("```", "").strip()

        # Load YAML to ensure it's valid
        parsed_yaml = yaml.safe_load(yaml_output)

        return parsed_yaml

    except Exception as e:
        st.error(f"Error parsing resume with OpenAI: {str(e)}")
        return {}

def upload_resume():
    """
    Streamlit interface for uploading and parsing resumes.
    """
    # Check for success message from previous upload
    if st.session_state.get('show_success', False):
        st.success("Parsed resume data saved successfully!")
        st.balloons()
        st.session_state.show_success = False

    st.subheader("Upload Your Resume")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])

    if uploaded_file is not None:
        file_type = uploaded_file.type
        st.write(f"**File Type:** {file_type}")

        if file_type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)
        elif file_type in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword"
        ]:
            text = extract_text_from_docx(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload a PDF or DOCX file.")
            return

        if not text.strip():
            st.error("No text found in the uploaded resume.")
            return

        st.subheader("Extracted Resume Text")
        with st.expander("View Extracted Text"):
            st.write(text[:2000] + ("..." if len(text) > 2000 else ""))  # Show first 2000 chars

        if st.button("Parse Resume"):
            with st.spinner("Parsing resume..."):
                parsed_data = parse_resume_with_openai(text)

            if parsed_data:
                st.subheader("Parsed Resume Data")
                yaml_display = yaml.dump(parsed_data, sort_keys=False)
                st.text_area("", yaml_display, height=600)

                if st.button("Save Parsed Data"):
                    try:
                        user_id = st.session_state.user['uid']
                        db.collection('users').document(user_id).set({
                            'parsed_resume': parsed_data
                        }, merge=True)
                        st.success("Parsed resume data saved successfully!")
                        st.balloons()  # Add a celebratory effect
                        st.session_state.show_success = True
                    except Exception as e:
                        st.error(f"Error saving data to Firestore: {str(e)}")
            else:
                st.error("Failed to parse resume data.")
