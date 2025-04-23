import os
import sys
import logging
import traceback
import streamlit as st
import tempfile
from tqdm import tqdm
from utils.document_processor import extract_resume_text
from utils.firecrawl_client import scrape_job_description, extract_company_info
from utils.anthropic_client import get_resume_suggestions, generate_cover_letter, create_interview_prep
from utils.resume_generator import generate_updated_resume
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("apply-here")

# Load environment variables
load_dotenv()
logger.info("Starting application...")

# Page configuration
st.set_page_config(
    page_title="Apply Here - Resume & Cover Letter Builder",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
try:
    with open('static/css/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    logger.info("Successfully loaded custom CSS")
except Exception as e:
    logger.error(f"Error loading CSS: {str(e)}")

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
        logger.info(f"Processing request for file: {resume_file.name}, job URL: {job_url}, company URL: {company_url}")
        temp_path = None
        try:
            # Create a temporary file to store the uploaded resume
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{resume_file.name.split('.')[-1]}") as temp_file:
                temp_file.write(resume_file.getvalue())
                temp_path = temp_file.name
            logger.info(f"Saved uploaded file to temp path: {temp_path}")
            
            # Set up progress tracking
            progress_bar = st.progress(0)
            progress_text = st.empty()
            
            # Extract text from resume
            progress_text.text("Extracting text from resume...")
            resume_text = extract_resume_text(temp_path)
            progress_bar.progress(20)
            
            # Get job description using Firecrawl API
            progress_text.text("Scraping job description...")
            job_description = scrape_job_description(job_url)
            progress_bar.progress(40)
            
            # Get company information using Firecrawl API
            progress_text.text("Extracting company information...")
            company_info = extract_company_info(company_url)
            progress_bar.progress(50)
            
            # Get suggestions for resume improvements
            progress_text.text("Generating resume suggestions...")
            resume_suggestions = get_resume_suggestions(resume_text, job_description)
            progress_bar.progress(70)
            
            # Generate updated resume
            progress_text.text("Creating updated resume...")
            updated_resume = generate_updated_resume(resume_text, resume_suggestions, job_description)
            
            # Generate cover letter
            progress_text.text("Generating cover letter...")
            cover_letter = generate_cover_letter(resume_text, job_description, company_info)
            progress_bar.progress(90)
            
            # Create interview prep sheet
            progress_text.text("Creating interview prep materials...")
            interview_prep = create_interview_prep(resume_text, job_description, company_info)
            progress_bar.progress(100)
            progress_text.text("Processing complete!")
            
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
                
            logger.info("Successfully processed request and generated all materials")
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            logger.error(traceback.format_exc())
            st.error(f"An error occurred: {str(e)}")
        
        finally:
            # Clean up the temporary file
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
                logger.info(f"Cleaned up temporary file: {temp_path}")
else:
    # Display instructions when the app first loads
    logger.info("Displaying initial instructions")
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
logger.info("Application UI rendered successfully")