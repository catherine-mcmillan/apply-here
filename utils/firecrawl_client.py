import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY")
FIRECRAWL_BASE_URL = "https://api.firecrawl.dev/api/v1"

def scrape_job_description(job_url):
    """
    Scrape job description from a URL using Firecrawl API's scrape endpoint
    
    Args:
        job_url (str): URL of the job posting
        
    Returns:
        str: Job description in a structured format
    """
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": job_url,
        "llm_ready": True  # Get the data in LLM-ready format
    }
    
    response = requests.post(
        f"{FIRECRAWL_BASE_URL}/scrape", 
        headers=headers, 
        json=payload
    )
    
    if response.status_code == 200:
        return response.json().get("content", "")
    else:
        raise Exception(f"Failed to scrape job description: {response.text}")

def extract_company_info(company_url):
    """
    Extract company information from a URL using Firecrawl API's extract endpoint
    
    Args:
        company_url (str): URL of the company website
        
    Returns:
        str: Extracted information about the company
    """
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": company_url,
        "extract": [
            "company_description",
            "products",
            "vision",
            "mission",
            "philosophy",
            "values"
        ],
        "llm_ready": True
    }
    
    response = requests.post(
        f"{FIRECRAWL_BASE_URL}/extract", 
        headers=headers, 
        json=payload
    )
    
    if response.status_code == 200:
        return response.json().get("content", "")
    else:
        raise Exception(f"Failed to extract company information: {response.text}")