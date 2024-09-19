import streamlit as st
from firebase_admin import firestore, initialize_app, credentials
from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from config import get_openai_api_key

# Initialize Firebase if not already initialized
try:
    db = firestore.client()
except ValueError:
    # Replace 'path/to/serviceAccountKey.json' with the actual path to your Firebase service account key
    cred = credentials.Certificate("path/to/serviceAccountKey.json")
    initialize_app(cred)
    db = firestore.client()

# Initialize OpenAI LLM
openai_api_key = get_openai_api_key()
llm = ChatOpenAI(temperature=0.7, model="gpt-4", openai_api_key=openai_api_key)

# Initialize Embeddings
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

def create_resume_index(resume_data):
    documents = []

    experience = resume_data.get('experience', '')
    if experience:
        documents.append(experience)

    skills = resume_data.get('skills', [])
    for skill in skills:
        documents.append(skill)

    vector_store = FAISS.from_texts(documents, embeddings)
    return vector_store

def generate_resume(resume_data, job_description):
    resume_index = create_resume_index(resume_data)

    query = "Identify the most relevant experiences and skills for the following job:"
    relevant_info = resume_index.similarity_search(
        f"{query}\n\n{job_description}", k=5)

    relevant_text = "\n".join([doc.page_content for doc in relevant_info])

    resume_template = """
    Given the following relevant resume information and job description, create a tailored resume:

    Relevant Resume Information:
    {relevant_info}

    Job Description:
    {job_description}

    Tailored Resume:
    """

    resume_prompt = PromptTemplate(
        input_variables=["relevant_info", "job_description"],
        template=resume_template)

    resume_chain = LLMChain(llm=llm, prompt=resume_prompt)
    tailored_resume = resume_chain.run(relevant_info=relevant_text,
                                       job_description=job_description)

    return tailored_resume

def generate_cover_letter(resume_data, job_description):
    resume_index = create_resume_index(resume_data)

    query = "Identify key qualifications and experiences relevant to the following job:"
    relevant_info = resume_index.similarity_search(
        f"{query}\n\n{job_description}", k=5)

    relevant_text = "\n".join([doc.page_content for doc in relevant_info])

    cover_letter_template = """
    Write a compelling cover letter for the following job based on the given relevant resume information:

    Relevant Resume Information:
    {relevant_info}

    Job Description:
    {job_description}

    Cover Letter:
    """

    cover_letter_prompt = PromptTemplate(
        input_variables=["relevant_info", "job_description"],
        template=cover_letter_template)

    cover_letter_chain = LLMChain(llm=llm, prompt=cover_letter_prompt)
    cover_letter = cover_letter_chain.run(relevant_info=relevant_text,
                                          job_description=job_description)

    return cover_letter

def generate_documents():
    st.subheader("Generate Tailored Resume and Cover Letter")

    user_id = st.session_state.get('user', {}).get('uid')
    if not user_id:
        st.warning("User not authenticated!")
        return

    user_doc = db.collection('users').document(user_id).get()

    if not user_doc.exists or 'resume_data' not in user_doc.to_dict():
        st.warning("Please upload your resume first!")
        return

    resume_data = user_doc.to_dict().get('resume_data', {})

    job_description = st.text_area("Paste the job description here:")

    if st.button("Generate Documents"):
        if not job_description.strip():
            st.warning("Please provide a job description.")
            return

        with st.spinner("Generating tailored resume and cover letter..."):
            tailored_resume = generate_resume(resume_data, job_description)
            cover_letter = generate_cover_letter(resume_data, job_description)

        st.subheader("Tailored Resume")
        st.text_area("", tailored_resume, height=300)

        st.subheader("Cover Letter")
        st.text_area("", cover_letter, height=300)

        if st.button("Save Generated Documents"):
            db.collection('users').document(user_id).set(
                {
                    'generated_documents': {
                        'resume': tailored_resume,
                        'cover_letter': cover_letter
                    }
                },
                merge=True)
            st.success("Documents saved successfully!")