import pytest
import requests
import responses
from utils.firecrawl_client import scrape_job_description, extract_company_info

@responses.activate
def test_scrape_job_description():
    """Test scraping a job description"""
    # Mock the Firecrawl API response
    responses.add(
        responses.POST,
        "https://api.firecrawl.dev/api/v1/scrape",
        json={"content": "Mocked job description content"},
        status=200
    )
    
    # Test the function
    result = scrape_job_description("https://example.com/job")
    
    assert result == "Mocked job description content"

@responses.activate
def test_scrape_job_description_error():
    """Test handling an error response from the Firecrawl API"""
    # Mock the Firecrawl API error response
    responses.add(
        responses.POST,
        "https://api.firecrawl.dev/api/v1/scrape",
        json={"error": "API error"},
        status=400
    )
    
    # Test that the function raises an exception
    with pytest.raises(Exception, match="Failed to scrape job description"):
        scrape_job_description("https://example.com/job")

@responses.activate
def test_extract_company_info():
    """Test extracting company information"""
    # Mock the Firecrawl API response
    responses.add(
        responses.POST,
        "https://api.firecrawl.dev/api/v1/extract",
        json={"content": "Mocked company info content"},
        status=200
    )
    
    # Test the function
    result = extract_company_info("https://example.com")
    
    assert result == "Mocked company info content"