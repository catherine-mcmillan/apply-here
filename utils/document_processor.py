import os
import docx
import PyPDF2
import re
import logging
from pylatexenc.latex2text import LatexNodes2Text
from pylatexenc.latexwalker import LatexWalkerError
from tqdm import tqdm

logger = logging.getLogger("apply-here.document_processor")

def extract_resume_text(file_path):
    """
    Extract text from various document formats (PDF, DOCX, DOC, TXT, LaTeX)
    
    Args:
        file_path (str): Path to the resume file
        
    Returns:
        str: Extracted text from the resume
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    with tqdm(total=100, desc=f"Extracting text from {os.path.basename(file_path)}", 
              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
        
        pbar.update(10)
        
        if file_extension == '.pdf':
            result = _extract_from_pdf(file_path)
        elif file_extension == '.docx':
            result = _extract_from_docx(file_path)
        elif file_extension == '.doc':
            # Note: Handling .doc files might require additional libraries
            raise NotImplementedError("DOC format support is not yet implemented")
        elif file_extension == '.txt':
            result = _extract_from_txt(file_path)
        elif file_extension == '.tex':
            result = _extract_from_latex(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        pbar.update(90)
        
    return result

def _extract_from_pdf(file_path):
    """Extract text from PDF file"""
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
    return text

def _extract_from_docx(file_path):
    """Extract text from DOCX file"""
    doc = docx.Document(file_path)
    return '\n'.join([paragraph.text for paragraph in doc.paragraphs])

def _extract_from_txt(file_path):
    """Extract text from TXT file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def _extract_from_latex(file_path):
    """Extract text from LaTeX file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            latex_content = file.read()
        
        logger.info(f"Processing LaTeX file: {file_path}")
        
        # Method 1: Use pylatexenc with error handling
        try:
            # Configure the converter with more tolerant settings
            converter = LatexNodes2Text(
                tolerant_parsing=True,
                strict_latex_spaces=False,
                keep_comments=False
            )
            return converter.latex_to_text(latex_content)
        except IndexError as e:
            logger.warning(f"IndexError in pylatexenc: {str(e)}. Falling back to simple extraction.")
        except LatexWalkerError as e:
            logger.warning(f"LatexWalkerError in pylatexenc: {str(e)}. Falling back to simple extraction.")
        except Exception as e:
            logger.warning(f"Unexpected error in pylatexenc: {str(e)}. Falling back to simple extraction.")
        
        # Method 2: Fallback to simple regex-based extraction if pylatexenc fails
        # Remove LaTeX commands and environments
        text = re.sub(r'\\[a-zA-Z]+(\{[^}]*\})*', ' ', latex_content)
        # Remove environment blocks 
        text = re.sub(r'\\begin\{[^}]*\}.*?\\end\{[^}]*\}', ' ', text, flags=re.DOTALL)
        # Remove curly braces
        text = re.sub(r'\{|\}', ' ', text)
        # Remove special characters
        text = re.sub(r'\\.|%.*$', ' ', text, flags=re.MULTILINE)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
        
    except Exception as e:
        logger.error(f"Error processing LaTeX file: {str(e)}")
        return f"Error extracting text from LaTeX: {str(e)}"