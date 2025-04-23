import pytest
from unittest.mock import patch, MagicMock
from utils.anthropic_client import get_resume_suggestions, generate_cover_letter, create_interview_prep, _extract_section

def test_extract_section():
    """Test extracting a section from XML-like text"""
    test_text = """
    <section1>This is content 1</section1>
    <section2>This is 
    multiline content 2</section2>
    <section3>This is content 3</section3>
    """
    
    result = _extract_section(test_text, "section2")
    assert result == "This is \nmultiline content 2"
    
    result = _extract_section(test_text, "section1")
    assert result == "This is content 1"
    
    result = _extract_section(test_text, "nonexistent")
    assert result == "Section not found in the response"

@patch('anthropic.Anthropic')
def test_get_resume_suggestions(mock_anthropic):
    """Test getting resume suggestions"""
    # Mock the Anthropic client and response
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_content = MagicMock()
    
    mock_content.text = """
    <language_suggestions>Improve bullet points</language_suggestions>
    <inclusion_questions>Add more projects?</inclusion_questions>
    <copy_edit_suggestions>Fix grammar</copy_edit_suggestions>
    <general_summary>Overall good</general_summary>
    """
    
    mock_response.content = [mock_content]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client
    
    # Test the function
    result = get_resume_suggestions("Resume text", "Job description")
    
    assert result["language_suggestions"] == "Improve bullet points"
    assert result["inclusion_questions"] == "Add more projects?"
    assert result["copy_edit_suggestions"] == "Fix grammar"
    assert result["general_summary"] == "Overall good"