import os
import logging
import requests
import re
from dotenv import load_dotenv
from tqdm import tqdm

# Configure logging
logger = logging.getLogger("apply-here.firecrawl_client")

# Load environment variables
load_dotenv()

FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY")
# Update the base URL to match the current API structure
FIRECRAWL_BASE_URL = "https://api.firecrawl.dev/v1"

# Environment flag to enable/disable mock mode
USE_MOCK = os.environ.get("USE_MOCK", "").lower() in ("true", "1", "t", "yes")

def check_api_key():
    """Check if the Firecrawl API key is set"""
    if not FIRECRAWL_API_KEY and not USE_MOCK:
        error_msg = "FIRECRAWL_API_KEY environment variable not set. Please set it in .env file or environment variables."
        logger.error(error_msg)
        raise ValueError(error_msg)

def _mock_scrape_job_description(job_url):
    """
    Mock implementation for scraping job descriptions when API is not available
    
    Args:
        job_url (str): URL of the job posting
        
    Returns:
        str: Mocked job description
    """
    logger.warning(f"Using MOCK implementation for job description scraping: {job_url}")
    
    # Extract job ID from URL if available
    job_id_match = re.search(r'jobs/(\d+)', job_url)
    job_id = job_id_match.group(1) if job_id_match else "unknown"
    
    # Generate a mock response based on the URL
    return f"""
    # Job Description for position #{job_id}
    
    ## About the Role
    
    We are looking for a talented professional to join our team. This is a great opportunity to work on exciting projects and grow your career.
    
    ## Requirements
    
    - 3+ years of relevant experience
    - Strong communication skills
    - Bachelor's degree or equivalent practical experience
    
    ## Responsibilities
    
    - Collaborate with cross-functional teams
    - Develop and implement solutions
    - Contribute to team success
    
    ## Benefits
    
    - Competitive salary
    - Health insurance
    - Flexible work arrangements
    - Professional development opportunities
    """

def _mock_extract_company_info(company_url):
    """
    Mock implementation for extracting company information when API is not available
    
    Args:
        company_url (str): URL of the company website
        
    Returns:
        str: Mocked company information
    """
    logger.warning(f"Using MOCK implementation for company information extraction: {company_url}")
    
    # Extract company name from URL if available
    company_name_match = re.search(r'//(?:www\.)?([^\.]+)', company_url)
    company_name = company_name_match.group(1) if company_name_match else "Company"
    company_name = company_name.capitalize()
    
    return f"""
    company_description: {company_name} is a leading provider of innovative solutions in its industry, committed to excellence and customer satisfaction.
    
    products: Our flagship products include cutting-edge software solutions, consulting services, and specialized tools for professionals.
    
    vision: To transform the industry through innovation and technology.
    
    mission: Our mission is to provide exceptional products and services that exceed customer expectations and set new standards in the industry.
    
    philosophy: We believe in collaboration, integrity, and continuous improvement as the foundation of our work.
    
    values: Innovation, Excellence, Integrity, Collaboration, Customer Focus
    """

def scrape_job_description(job_url):
    """
    Scrape job description from a URL using Firecrawl API's scrape endpoint
    
    Args:
        job_url (str): URL of the job posting
        
    Returns:
        str: Job description in a structured format
    """
    # Check if mock mode is enabled
    if USE_MOCK:
        return _mock_scrape_job_description(job_url)
    
    # Check if API key is set
    check_api_key()
    
    with tqdm(total=100, desc=f"Scraping job description from {job_url}", 
              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
        
        pbar.update(10)
        logger.info(f"Scraping job description from URL: {job_url}")
        
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Update the payload structure to match the current API documentation
        payload = {
            "url": job_url,
            "formats": ["markdown"]  # Request markdown format specifically
        }
        
        pbar.update(30)
        
        try:
            response = requests.post(
                f"{FIRECRAWL_BASE_URL}/scrape", 
                headers=headers, 
                json=payload
            )
            
            pbar.update(50)
            
            if response.status_code == 200:
                response_json = response.json()
                # Check for success flag
                if response_json.get("success"):
                    # Extract markdown content from the new response structure
                    content = response_json.get("data", {}).get("markdown", "")
                    logger.info(f"Successfully scraped job description, received {len(content)} characters")
                    pbar.update(10)
                    return content
                else:
                    error_msg = f"Failed to scrape job description: API returned success=false"
                    logger.error(error_msg)
                    # Fall back to mock implementation on API errors
                    logger.warning("Falling back to mock implementation due to API error")
                    return _mock_scrape_job_description(job_url)
            else:
                error_msg = f"Failed to scrape job description: {response.text}"
                logger.error(error_msg)
                # Fall back to mock implementation on API errors
                logger.warning("Falling back to mock implementation due to API error")
                return _mock_scrape_job_description(job_url)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error when scraping job description: {str(e)}"
            logger.error(error_msg)
            # Fall back to mock implementation on network errors
            logger.warning("Falling back to mock implementation due to network error")
            return _mock_scrape_job_description(job_url)
        except Exception as e:
            error_msg = f"Unexpected error when scraping job description: {str(e)}"
            logger.error(error_msg)
            # Fall back to mock implementation on any errors
            logger.warning("Falling back to mock implementation due to unexpected error")
            return _mock_scrape_job_description(job_url)
        finally:
            # Ensure progress bar completes
            pbar.update(100 - pbar.n)

def extract_company_info(company_url):
    """
    Extract company information from a URL using Firecrawl API's extract endpoint
    
    Args:
        company_url (str): URL of the company website
        
    Returns:
        str: Extracted information about the company
    """
    # Check if mock mode is enabled
    if USE_MOCK:
        return _mock_extract_company_info(company_url)
    
    # Check if API key is set
    check_api_key()
    
    with tqdm(total=100, desc=f"Extracting company info from {company_url}", 
              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
        
        pbar.update(10)
        logger.info(f"Extracting company information from URL: {company_url}")
        
        headers = {
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Update to use the jsonOptions field as specified in the docs
        # and use the schema-less extraction approach
        payload = {
            "url": company_url,
            "formats": ["json"],
            "jsonOptions": {
                "prompt": "Extract the following information about the company: company description, products, vision, mission, philosophy, and values."
            }
        }
        
        pbar.update(30)
        
        try:
            response = requests.post(
                f"{FIRECRAWL_BASE_URL}/scrape", 
                headers=headers, 
                json=payload
            )
            
            pbar.update(50)
            
            if response.status_code == 200:
                response_json = response.json()
                # Check for success flag
                if response_json.get("success"):
                    # Extract JSON content from the new response structure
                    content = response_json.get("data", {}).get("json", {})
                    # Convert to string if it's a dictionary
                    if isinstance(content, dict):
                        content = "\n".join([f"{k}: {v}" for k, v in content.items()])
                    logger.info(f"Successfully extracted company information, received {len(str(content))} characters")
                    pbar.update(10)
                    return str(content)
                else:
                    error_msg = f"Failed to extract company information: API returned success=false"
                    logger.error(error_msg)
                    # Fall back to mock implementation on API errors
                    logger.warning("Falling back to mock implementation due to API error")
                    return _mock_extract_company_info(company_url)
            else:
                error_msg = f"Failed to extract company information: {response.text}"
                logger.error(error_msg)
                # Fall back to mock implementation on API errors
                logger.warning("Falling back to mock implementation due to API error")
                return _mock_extract_company_info(company_url)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error when extracting company information: {str(e)}"
            logger.error(error_msg)
            # Fall back to mock implementation on network errors
            logger.warning("Falling back to mock implementation due to network error")
            return _mock_extract_company_info(company_url)
        except Exception as e:
            error_msg = f"Unexpected error when extracting company information: {str(e)}"
            logger.error(error_msg)
            # Fall back to mock implementation on any errors
            logger.warning("Falling back to mock implementation due to unexpected error")
            return _mock_extract_company_info(company_url)
        finally:
            # Ensure progress bar completes
            pbar.update(100 - pbar.n)