import streamlit as st
from firebase_admin import firestore
import firebase_admin
from firebase_admin import credentials
from pdfminer.high_level import extract_text
from docx import Document
import yaml
import openai
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

# Initialize OpenAI API
openai.api_key = config.get_openai_api_key()

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
    try:
        # Read the YAML template from the file
        template_path = "plain_text_resume.yaml"
        if not os.path.exists(template_path):
            st.error(f"YAML template file '{template_path}' not found.")
            return {}

        with open(template_path, "r") as file:
            yaml_template = file.read()

        prompt = f"""
        You are an AI assistant that extracts information from resumes and structures it into a predefined YAML format. Below is the extracted text from a resume. Please fill in the YAML template accurately based on the information provided.

        Extracted Resume Text:
        \"\"\"
        {text}
        \"\"\"

        YAML Template:
        ```yaml
        {yaml_template}
        Please ensure that the YAML syntax is correct. If certain fields are not present in the resume text, leave them as empty strings or omit them.

        Output the YAML only without any additional text. """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that structures resume information into YAML format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=2000,
            n=1,
            stop=None,
        )

        yaml_output = response.choices[0].message['content']

        # Ensure that only YAML content is captured
        if '```yaml' in yaml_output and '```' in yaml_output:
            yaml_content = yaml_output.split('```yaml')[1].split('```')[0]
        else:
            yaml_content = yaml_output

        # Load YAML to ensure it's valid
        parsed_yaml = yaml.safe_load(yaml_content)

        return parsed_yaml

    except Exception as e:
        st.error(f"Error parsing resume with OpenAI: {str(e)}")
        return {}

def upload_resume():
    """Streamlit interface for uploading and parsing resumes."""
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

                # Buttons for saving data
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Save Parsed Data to Firestore"):
                        try:
                            # Ensure user is authenticated
                            if 'user' not in st.session_state:
                                st.error("You need to be logged in to save data.")
                            else:
                                user_id = st.session_state.user['uid']
                                db.collection('users').document(user_id).set({
                                    'parsed_resume': parsed_data
                                }, merge=True)
                                st.success("Parsed resume data saved to Firestore successfully!")
                        except Exception as e:
                            st.error(f"Error saving data to Firestore: {str(e)}")
                with col2:
                    if st.button("Save to YAML File"):
                        try:
                            with open("filled_resume.yaml", "w") as yaml_file:
                                yaml.dump(parsed_data, yaml_file, sort_keys=False)
                            st.success("Parsed resume data saved to filled_resume.yaml successfully!")
                        except Exception as e:
                            st.error(f"Error saving data to YAML file: {str(e)}")
            else:
                st.error("Failed to parse resume data.")
