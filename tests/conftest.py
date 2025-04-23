import pytest
import os
import tempfile

@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing"""
    # In a real test, you would create an actual PDF file
    # For this example, we'll just create an empty file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(b'%PDF-1.5\nMock PDF content')
        path = f.name
    
    yield path
    
    # Clean up
    os.unlink(path)

@pytest.fixture
def sample_text_file():
    """Create a sample text file for testing"""
    content = "John Doe\nSoftware Engineer\n\nExperience:\n- Company A: Senior Developer\n- Company B: Junior Developer"
    
    with tempfile.NamedTemporaryFile(suffix='.txt', mode='w', delete=False) as f:
        f.write(content)
        path = f.name
    
    yield path
    
    # Clean up
    os.unlink(path)

@pytest.fixture
def mock_job_description():
    """Sample job description for testing"""
    return """
    Software Engineer Position
    
    Requirements:
    - 3+ years of experience in Python development
    - Experience with web frameworks
    - Knowledge of cloud platforms
    
    Responsibilities:
    - Develop and maintain web applications
    - Work with cross-functional teams
    - Optimize application performance
    """

@pytest.fixture
def mock_company_info():
    """Sample company information for testing"""
    return """
    Company: ABC Tech
    
    About Us:
    ABC Tech is a leading software company focused on innovation.
    
    Our Mission:
    To create software that improves lives.
    
    Values:
    - Innovation
    - Collaboration
    - Excellence
    """