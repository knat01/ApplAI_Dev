import streamlit as st
from firebase_admin import firestore
from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
from llama_index import GPTSimpleVectorIndex, Document
from config import OPENAI_API_KEY

db = firestore.client()

# Initialize OpenAI LLM
llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o", openai_api_key=OPENAI_API_KEY)

def create_resume_index(resume_data):
    documents = [Document(resume_data['experience'])]
    for skill in resume_data['skills']:
        documents.append(Document(skill))
    return GPTSimpleVectorIndex(documents)

def generate_resume(resume_data, job_description):
    resume_index = create_resume_index(resume_data)
    
    resume_template = """
    Given the following resume data and job description, create a tailored resume:

    Resume data:
    {resume_data}

    Job description:
    {job_description}

    Tailored resume:
    """

    resume_prompt = PromptTemplate(
        input_variables=["resume_data", "job_description"],
        template=resume_template
    )

    resume_chain = LLMChain(llm=llm, prompt=resume_prompt)
    
    tailored_resume = resume_chain.run(resume_data=str(resume_data), job_description=job_description)
    return tailored_resume

def generate_cover_letter(resume_data, job_description):
    cover_letter_template = """
    Write a compelling cover letter for the following job based on the given resume data:

    Resume data:
    {resume_data}

    Job description:
    {job_description}

    Cover letter:
    """

    cover_letter_prompt = PromptTemplate(
        input_variables=["resume_data", "job_description"],
        template=cover_letter_template
    )

    cover_letter_chain = LLMChain(llm=llm, prompt=cover_letter_prompt)
    
    cover_letter = cover_letter_chain.run(resume_data=str(resume_data), job_description=job_description)
    return cover_letter

def generate_documents():
    st.subheader("Generate Tailored Resume and Cover Letter")
    
    user_id = st.session_state.user['uid']
    user_doc = db.collection('users').document(user_id).get()
    
    if not user_doc.exists or 'resume_data' not in user_doc.to_dict():
        st.warning("Please upload your resume first!")
        return

    resume_data = user_doc.to_dict()['resume_data']
    
    job_description = st.text_area("Paste the job description here:")
    
    if st.button("Generate Documents"):
        with st.spinner("Generating tailored resume and cover letter..."):
            tailored_resume = generate_resume(resume_data, job_description)
            cover_letter = generate_cover_letter(resume_data, job_description)
        
        st.subheader("Tailored Resume")
        st.text_area("", tailored_resume, height=300)
        
        st.subheader("Cover Letter")
        st.text_area("", cover_letter, height=300)
        
        if st.button("Save Generated Documents"):
            db.collection('users').document(user_id).set({
                'generated_documents': {
                    'resume': tailored_resume,
                    'cover_letter': cover_letter
                }
            }, merge=True)
            st.success("Documents saved successfully!")
