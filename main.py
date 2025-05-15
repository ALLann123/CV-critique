#!/usr/bin/python3
import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


api_key = os.getenv("GITHUB_TOKEN")

# Create the LangChain chat model using the GitHub Marketplace endpoint

st.set_page_config(page_title="AI Resume Critiquer", page_icon="📄", layout="centered")

st.title("🤖Resume Critiquer")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")


uploaded_file=st.file_uploader("Upload your resume (PDF of TXT)", type=["pdf", "txt"])
job_role=st.text_input("Enter the job role you're targetting(Option)")

analyze=st.button("Analyze Resume")

def extract_text_from_pdf(pdf_file):
    pdf_reader=PyPDF2.PdfReader(pdf_file)
    text=""
    for page in pdf_reader.pages:
        text+=page.extract_text() + "\n"
    return text


def extract_text_from_file(uploaded_file):
    file_type = uploaded_file.type

    if file_type == "application/pdf":
        pdf_bytes = io.BytesIO(uploaded_file.read())
        return extract_text_from_pdf(pdf_bytes)
    return uploaded_file.read().decode("utf-8")

if analyze and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("File does not have any content...")
            st.stop()

        prompt = f"""Please analyze this resume and provide constructive feedback. 
        Focus on the following aspects:
        1. Content clarity and impact
        2. Skills presentation
        3. Experience descriptions
        4. Specific improvements for {job_role if job_role else 'general job applications'}
        
        Resume content:
        {file_content}
        
        Please provide your analysis in a clear, structured format with specific recommendations."""
        
        client = OpenAI(api_key=api_key,base_url="https://models.inference.ai.azure.com")
        response=client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role":"system", "content": "You are an expert resume reviewer with years of experience in HR and recruitement."},
                {"role": "user", "content":prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        st.markdown("###Analysis Results")
        st.markdown(response.choices[0].message.content)
    
    except Exception as e:
        st.error(f"An error occured: {str(e)}")

