import os
import streamlit as st
import tempfile
from utils.document_processor import extract_resume_text
from utils.firecrawl_client import scrape_job_description, extract_company_info
from utils.anthropic_client import get_resume_suggestions, generate_cover_letter, create_interview_prep
from utils.resume_generator import generate_updated_resume
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Apply Here - Resume & Cover Letter Builder",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
with open('static/css/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# App header
st.title("Apply Here")
st.subheader("Resume & Cover Letter Builder")
st.markdown("Optimize your job application with AI-powered suggestions!")

# Sidebar for inputs
with st.sidebar:
    st.header("Upload Your Information")
    
    # Resume upload
    resume_file = st.file_uploader("Upload your resume", type=["pdf", "docx", "doc", "txt", "tex"])
    
    # Job description URL
    job_url = st.text_input("Job Description URL")
    
    # Company website
    company_url = st.text_input("Company Website URL")
    
    # Process button
    process_button = st.button("Generate Application Materials")

# Main content area
if process_button and resume_file and job_url and company_url:
    with st.spinner("Processing your application materials..."):
        # Create a temporary file to store the uploaded resume
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{resume_file.name.split('.')[-1]}") as temp_file:
            temp_file.write(resume_file.getvalue())
            temp_path = temp_file.name
        
        try:
            # Extract text from resume
            resume_text = extract_resume_text(temp_path)
            
            # Get job description using Firecrawl API
            job_description = scrape_job_description(job_url)
            
            # Get company information using Firecrawl API
            company_info = extract_company_info(company_url)
            
            # Get suggestions for resume improvements
            resume_suggestions = get_resume_suggestions(resume_text, job_description)
            
            # Generate updated resume
            updated_resume = generate_updated_resume(resume_text, resume_suggestions, job_description)
            
            # Generate cover letter
            cover_letter = generate_cover_letter(resume_text, job_description, company_info)
            
            # Create interview prep sheet
            interview_prep = create_interview_prep(resume_text, job_description, company_info)
            
            # Display results in tabs
            tab1, tab2, tab3, tab4 = st.tabs(["Resume Suggestions", "Updated Resume", "Cover Letter", "Interview Prep"])
            
            with tab1:
                st.header("Resume Suggestions")
                st.markdown("### Language Suggestions")
                st.write(resume_suggestions["language_suggestions"])
                
                st.markdown("### Inclusion Questions")
                st.write(resume_suggestions["inclusion_questions"])
                
                st.markdown("### Copy Edit Suggestions")
                st.write(resume_suggestions["copy_edit_suggestions"])
                
                st.markdown("### General Summary")
                st.write(resume_suggestions["general_summary"])
            
            with tab2:
                st.header("Updated Resume")
                st.text_area("", updated_resume, height=500)
                st.download_button("Download Updated Resume", updated_resume, "updated_resume.txt")
            
            with tab3:
                st.header("Cover Letter")
                st.text_area("", cover_letter, height=500)
                st.download_button("Download Cover Letter", cover_letter, "cover_letter.txt")
            
            with tab4:
                st.header("Interview Prep Cheat Sheet")
                st.text_area("", interview_prep, height=500)
                st.download_button("Download Interview Prep", interview_prep, "interview_prep.txt")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
else:
    # Display instructions when the app first loads
    st.markdown("""
    ## How to Use This Tool
    
    1. **Upload your resume** (supported formats: PDF, DOCX, DOC, TXT, LaTeX)
    2. **Enter the job description URL** you're applying for
    3. **Enter the company website URL** to tailor your application
    4. Click **Generate Application Materials** to create your customized application package
    
    You'll receive:
    - Suggestions to improve your resume
    - An updated resume tailored to the job
    - A customized cover letter
    - An interview prep cheat sheet
    """)

# Footer
st.markdown("---")
st.markdown("© 2023 Apply Here | Powered by Anthropic Claude & Firecrawl")