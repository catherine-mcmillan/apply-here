import pytest
from utils.document_processor import extract_resume_text, _extract_from_txt

def test_extract_from_txt(sample_text_file):
    """Test extracting text from a text file"""
    # Get the expected content
    with open(sample_text_file, 'r') as f:
        expected_content = f.read()
    
    # Test the extraction function
    extracted_text = _extract_from_txt(sample_text_file)
    
    assert extracted_text == expected_content
    assert "John Doe" in extracted_text
    assert "Software Engineer" in extracted_text
    assert "Company A" in extracted_text

def test_extract_resume_text_with_txt(sample_text_file):
    """Test extracting text from a resume in text format"""
    extracted_text = extract_resume_text(sample_text_file)
    
    assert "John Doe" in extracted_text
    assert "Software Engineer" in extracted_text
    assert "Experience" in extracted_text

def test_unsupported_format():
    """Test that an unsupported format raises an error"""
    with pytest.raises(ValueError, match="Unsupported file format"):
        extract_resume_text("resume.unsupported")