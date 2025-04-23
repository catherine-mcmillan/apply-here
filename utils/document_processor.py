import os
import docx
import PyPDF2
import re
from pylatexenc.latex2text import LatexNodes2Text

def extract_resume_text(file_path):
    """
    Extract text from various document formats (PDF, DOCX, DOC, TXT, LaTeX)
    
    Args:
        file_path (str): Path to the resume file
        
    Returns:
        str: Extracted text from the resume
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        return _extract_from_pdf(file_path)
    elif file_extension == '.docx':
        return _extract_from_docx(file_path)
    elif file_extension == '.doc':
        # Note: Handling .doc files might require additional libraries
        raise NotImplementedError("DOC format support is not yet implemented")
    elif file_extension == '.txt':
        return _extract_from_txt(file_path)
    elif file_extension == '.tex':
        return _extract_from_latex(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

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
    with open(file_path, 'r', encoding='utf-8') as file:
        latex_content = file.read()
    
    # Convert LaTeX to plain text
    converter = LatexNodes2Text()
    return converter.latex_to_text(latex_content)