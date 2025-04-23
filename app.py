import os
import sys
import logging
import traceback
import streamlit as st
import tempfile
import base64
import subprocess
from tqdm import tqdm
from utils.document_processor import extract_resume_text
from utils.firecrawl_client import scrape_job_description, extract_company_info
from utils.anthropic_client import get_resume_suggestions, generate_cover_letter, create_interview_prep
from utils.resume_generator import generate_updated_resume
from dotenv import load_dotenv
import re

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

# Add LaTeX CSS
st.markdown("""
<style>
.latex-container {
    font-family: 'Latin Modern Roman', 'Times New Roman', serif;
    line-height: 1.5;
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 5px;
    border: 1px solid #e0e0e0;
    overflow-y: auto;
    max-height: 600px;
}

.latex-code {
    font-family: 'Source Code Pro', monospace;
    padding: 10px;
    background-color: #f1f1f1;
    border-radius: 5px;
    font-size: 0.9em;
    white-space: pre-wrap;
    overflow-x: auto;
}

.tabs-container {
    margin-bottom: 20px;
}

.tab-button {
    padding: 10px 20px;
    background-color: #f1f1f1;
    border: none;
    cursor: pointer;
    margin-right: 2px;
    border-radius: 5px 5px 0 0;
    font-weight: 500;
}

.tab-button.active {
    background-color: #4338ca;
    color: white;
}

.tab-content {
    display: none;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 0 5px 5px 5px;
}

.tab-content.active {
    display: block;
}
</style>
""", unsafe_allow_html=True)

# Function to generate a PDF from LaTeX
def generate_pdf_from_latex(latex_code):
    """
    Generate a PDF from LaTeX code using pdflatex
    
    Args:
        latex_code (str): LaTeX code
        
    Returns:
        str: Path to the generated PDF file or None if generation failed
    """
    try:
        # Create a temporary directory for LaTeX files
        temp_dir = tempfile.mkdtemp()
        temp_tex_path = os.path.join(temp_dir, "resume.tex")
        
        # Write the LaTeX code to a temporary file
        with open(temp_tex_path, "w") as f:
            f.write(latex_code)
        
        # Run pdflatex to compile the LaTeX file
        process = subprocess.Popen(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", temp_dir, temp_tex_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        _, stderr = process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Error generating PDF: {stderr.decode('utf-8')}")
            return None
        
        # Return the path to the generated PDF
        return os.path.join(temp_dir, "resume.pdf")
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return None

# Function to create a download link for a file
def get_download_link(file_path, file_name, link_text):
    """
    Create a download link for a file
    
    Args:
        file_path (str): Path to the file
        file_name (str): Name to save the file as
        link_text (str): Text to display for the link
        
    Returns:
        str: HTML for a download link
    """
    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        b64 = base64.b64encode(file_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">{link_text}</a>'
        return href
    except Exception as e:
        logger.error(f"Error creating download link: {str(e)}")
        return None

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
            updated_resume_latex = generate_updated_resume(resume_text, resume_suggestions, job_description)
            
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
                st.header("Updated Resume (LaTeX Format)")
                
                # Create two columns for LaTeX code and preview
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("LaTeX Source")
                    
                    # Extract the content part of the LaTeX (exclude preamble and document tags)
                    latex_content = updated_resume_latex
                    
                    # Extract just the content between \begin{document} and \end{document}
                    begin_idx = updated_resume_latex.find("\\begin{document}")
                    end_idx = updated_resume_latex.find("\\end{document}")
                    
                    if begin_idx != -1 and end_idx != -1:
                        # Get the content between the tags, excluding the tags themselves
                        begin_idx += len("\\begin{document}")
                        latex_content = updated_resume_latex[begin_idx:end_idx].strip()
                    
                    # Display the LaTeX content in a code block
                    st.code(latex_content, language="latex")
                    
                    # Download buttons for various formats
                    col1a, col1b = st.columns(2)
                    with col1a:
                        st.download_button(
                            "Download .tex file",
                            updated_resume_latex,
                            file_name="resume.tex",
                            mime="application/x-tex"
                        )
                
                with col2:
                    st.subheader("Preview")
                    
                    # Create a more visually appealing preview with proper formatting
                    st.markdown('<div class="latex-container" style="font-family: \'Times New Roman\', serif; line-height: 1.5;">', unsafe_allow_html=True)
                    
                    # Create a representation that looks more like a rendered LaTeX document
                    # Extract name from the LaTeX code
                    name_match = re.search(r'\\name\{(.*?)\}\{(.*?)\}', updated_resume_latex)
                    if name_match:
                        first_name = name_match.group(1)
                        last_name = name_match.group(2)
                        full_name = f"{first_name} {last_name}"
                        st.markdown(f'<h1 style="text-align: center; font-size: 1.8rem; margin-bottom: 1rem;">{full_name}</h1>', unsafe_allow_html=True)
                    
                    # Extract contact information
                    contact_info = []
                    email_match = re.search(r'\\email\{(.*?)\}', updated_resume_latex)
                    if email_match:
                        contact_info.append(f'<span style="margin-right: 1rem;">📧 {email_match.group(1)}</span>')
                    
                    phone_match = re.search(r'\\phone\{(.*?)\}', updated_resume_latex)
                    if phone_match:
                        contact_info.append(f'<span style="margin-right: 1rem;">📱 {phone_match.group(1)}</span>')
                    
                    linkedin_match = re.search(r'\\social\[linkedin\]\{(.*?)\}', updated_resume_latex)
                    if linkedin_match:
                        contact_info.append(f'<span>🔗 {linkedin_match.group(1)}</span>')
                    
                    if contact_info:
                        st.markdown(f'<div style="text-align: center; margin-bottom: 1.5rem;">{" ".join(contact_info)}</div>', unsafe_allow_html=True)
                    
                    # Process sections and content using regex patterns
                    sections = []
                    
                    # Find all sections
                    section_matches = re.finditer(r'\\section\{(.*?)\}(.*?)(?=\\section\{|\\end\{document\})', updated_resume_latex, re.DOTALL)
                    
                    for section_match in section_matches:
                        section_name = section_match.group(1)
                        section_content = section_match.group(2).strip()
                        
                        section_html = f'<h2 style="color: #4338ca; border-bottom: 1px solid #ddd; padding-bottom: 0.3rem; margin-top: 1.5rem;">{section_name}</h2>'
                        
                        # Process subsections
                        subsection_matches = re.finditer(r'\\subsection\{(.*?)\}', section_content)
                        # Process cventries
                        cventry_matches = re.finditer(r'\\cventry\{(.*?)\}\{(.*?)\}\{(.*?)\}\{(.*?)\}\{(.*?)\}\{(.*?)\}', section_content)
                        # Process itemize blocks
                        itemize_blocks = re.finditer(r'\\begin\{itemize\}(.*?)\\end\{itemize\}', section_content, re.DOTALL)
                        
                        # Process subsections first
                        for subsection_match in subsection_matches:
                            subsection_name = subsection_match.group(1)
                            section_html += f'<h3 style="color: #1f2937; margin-top: 1rem; margin-bottom: 0.5rem;">{subsection_name}</h3>'
                        
                        # Process CVEntries
                        for cventry_match in cventry_matches:
                            date = cventry_match.group(1)
                            title = cventry_match.group(2)
                            organization = cventry_match.group(3)
                            location = cventry_match.group(4)
                            
                            section_html += f'''
                            <div style="margin-bottom: 1rem;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                                    <span style="font-weight: bold;">{title}</span>
                                    <span>{date}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between;">
                                    <span style="font-style: italic;">{organization}</span>
                                    <span>{location}</span>
                                </div>
                            </div>
                            '''
                        
                        # Process itemize blocks
                        for itemize_block in itemize_blocks:
                            items_content = itemize_block.group(1)
                            # Improved regex to better handle item content with special characters and multiple lines
                            items = re.finditer(r'\\item\s+(.*?)(?=\\item|\\end{itemize}|$)', items_content, re.DOTALL)
                            
                            section_html += '<ul style="margin-left: 1.5rem; margin-bottom: 1rem;">'
                            for item in items:
                                item_text = item.group(1).strip()
                                # Remove any remaining LaTeX commands
                                item_text = re.sub(r'\\[a-zA-Z]+(\{[^}]*\})*', '', item_text)
                                section_html += f'<li style="margin-bottom: 0.25rem;">{item_text}</li>'
                            section_html += '</ul>'
                        
                        sections.append(section_html)
                    
                    # Join all sections together
                    if sections:
                        st.markdown(''.join(sections), unsafe_allow_html=True)
                    else:
                        st.info("Unable to parse LaTeX content for preview. Please download the .tex file and compile it.")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Add note about LaTeX compilation
                    st.info("For full LaTeX rendering, download the .tex file and compile it with pdflatex or use an online LaTeX editor like Overleaf.")
                    
                    # Add link to online LaTeX editor
                    st.markdown("""
                    <a href="https://www.overleaf.com/docs?snip_uri=https://example.com/resume.tex" target="_blank" style="text-decoration: none;">
                        <div style="border-radius: 4px; background-color: #f2f2f2; padding: 8px 16px; display: inline-block; cursor: pointer; margin-top: 10px;">
                            <span style="color: #4338ca; font-weight: 500;">Open in Overleaf</span>
                        </div>
                    </a>
                    """, unsafe_allow_html=True)
            
            with tab3:
                st.header("Cover Letter")
                # Render the cover letter with nicer formatting
                st.markdown('<div class="markdown-content">', unsafe_allow_html=True)
                formatted_cover_letter = cover_letter.replace('\n', '<br>')
                st.markdown(f"<p>{formatted_cover_letter}</p>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.download_button("Download Cover Letter", cover_letter, "cover_letter.txt")
            
            with tab4:
                st.header("Interview Prep Cheat Sheet")
                # Render the interview prep as markdown
                st.markdown('<div class="markdown-content">', unsafe_allow_html=True)
                st.markdown(interview_prep)
                st.markdown('</div>', unsafe_allow_html=True)
                st.download_button("Download Interview Prep", interview_prep, "interview_prep.md")
                
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
    - An updated resume tailored to the job in LaTeX format
    - A customized cover letter
    - An interview prep cheat sheet
    """)

# Footer
st.markdown("---")
st.markdown("© 2023 Apply Here | Powered by Anthropic Claude & Firecrawl")
logger.info("Application UI rendered successfully")