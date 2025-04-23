import os
import anthropic
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-3-7-sonnet-20250219"  # Use the latest model as mentioned in the documentation

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def get_resume_suggestions(resume_text, job_description):
    """
    Get suggestions for improving the resume based on the job description
    
    Args:
        resume_text (str): Text extracted from the resume
        job_description (str): Text extracted from the job posting
        
    Returns:
        dict: Dictionary containing different categories of suggestions
    """
    system_prompt = "You are a professional Resume coach. Your job is to help candidates tailor their resume to fit a job description and highlight their skills in the best light. You should also attempt to keep them human and approachable."
    
    user_prompt = f"""You are an expert resume reviewer tasked with providing a comprehensive review of a resume. Your goal is to help improve the resume and assess its fit for a potential job opportunity. Follow these instructions carefully:

1. First, carefully read and analyze the contents of the resume provided in the following La-Tex formatted resume:
<resume_La-Tex>
{resume_text}
</resume_La-Tex>

2. If a job description is provided, read and analyze it as well:
<job_description>
{job_description}
</job_description>

3. If a job description is provided, compare the resume to the job requirements and responsibilities. Identify areas where the resume aligns well with the job description and areas where it could be improved to better match the position.

4. Provide options for revised professional summaries.

5. If no job description is provided, focus on general best practices for resume writing and industry standards.

6. Based on your analysis, provide the following:

   a. Suggestions for improving the language and content of the resume. If a job description is provided, focus on aligning the resume more closely with the job requirements.
   
   b. Questions about possible items to include or highlight, including suggestions for adding additional metrics or quantifiable achievements.
   
   c. Copy editing suggestions for grammar, spelling, formatting, and overall presentation.

7. Provide a general summary of the resume's strengths and weaknesses, and if a job description is provided, an assessment of the candidate's fit for the position.

8. Organize your review into the following sections, using appropriate XML tags:

   <language_suggestions>
   Provide suggestions for improving the language and content of the resume.
   </language_suggestions>

   <inclusion_questions>
   List questions about possible items to include or highlight, including suggestions for adding metrics.
   </inclusion_questions>

   <copy_edit_suggestions>
   Offer copy editing suggestions for grammar, spelling, formatting, and overall presentation.
   </copy_edit_suggestions>

   <general_summary>
   Provide a general summary of the resume's strengths and weaknesses, and if applicable, an assessment of the candidate's fit for the position.
   </general_summary>

9. Your final output should only include the content within these four XML tags. Do not include any additional commentary or notes outside of these sections."""

    # Call Anthropic API
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=20000,
        temperature=1,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    }
                ]
            }
        ]
    )
    
    # Extract the content from the response
    response_text = response.content[0].text
    
    # Parse the XML-like structure to extract the sections
    language_suggestions = _extract_section(response_text, "language_suggestions")
    inclusion_questions = _extract_section(response_text, "inclusion_questions")
    copy_edit_suggestions = _extract_section(response_text, "copy_edit_suggestions")
    general_summary = _extract_section(response_text, "general_summary")
    
    return {
        "language_suggestions": language_suggestions,
        "inclusion_questions": inclusion_questions,
        "copy_edit_suggestions": copy_edit_suggestions,
        "general_summary": general_summary
    }

def generate_cover_letter(resume_text, job_description, company_info):
    """
    Generate a cover letter based on the resume, job description, and company information
    
    Args:
        resume_text (str): Text extracted from the resume
        job_description (str): Text extracted from the job posting
        company_info (str): Information about the company
        
    Returns:
        str: Generated cover letter
    """
    system_prompt = "You are a professional cover letter writer. Your job is to help candidates create compelling, tailored cover letters that showcase their qualifications and align with the company's values and needs."
    
    user_prompt = f"""Create a professional, tailored cover letter based on the candidate's resume, the job description, and information about the company. Follow these instructions:

1. Review the candidate's resume:
<resume>
{resume_text}
</resume>

2. Analyze the job description:
<job_description>
{job_description}
</job_description>

3. Consider the company information:
<company_info>
{company_info}
</company_info>

4. Create a cover letter that:
   - Is professionally formatted with appropriate sections
   - Starts with a compelling introduction
   - Highlights the candidate's most relevant skills and experiences for this specific position
   - Demonstrates knowledge of the company and why the candidate is interested in working there
   - Includes a strong closing paragraph
   - Is between 250-400 words
   - Uses a professional but conversational tone
   - Avoids clichés and generic statements
   - Includes specific examples that demonstrate the candidate's qualifications
   - References company values or mission when relevant

5. Do not include placeholder text, all information should be specific to this candidate and position.

6. Format the cover letter with proper spacing and structure.

Output only the completed cover letter text with no additional explanations or notes."""

    # Call Anthropic API
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4000,
        temperature=0.7,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    }
                ]
            }
        ]
    )
    
    # Return the generated cover letter
    return response.content[0].text

def create_interview_prep(resume_text, job_description, company_info):
    """
    Create an interview prep cheat sheet based on the resume, job description, and company information
    
    Args:
        resume_text (str): Text extracted from the resume
        job_description (str): Text extracted from the job posting
        company_info (str): Information about the company
        
    Returns:
        str: Generated interview prep cheat sheet
    """
    system_prompt = "You are a professional interview coach. Your job is to help candidates prepare for job interviews by providing them with tailored preparation materials and insights."
    
    user_prompt = f"""Create a comprehensive interview prep cheat sheet for a candidate based on their resume, the job description, and company information. Follow these instructions:

1. Review the candidate's resume:
<resume>
{resume_text}
</resume>

2. Analyze the job description:
<job_description>
{job_description}
</job_description>

3. Consider the company information:
<company_info>
{company_info}
</company_info>

4. Create an interview prep cheat sheet that includes:

   <key_talking_points>
   List 5-7 key accomplishments from the resume that align with the job requirements. For each point, provide a concise STAR format (Situation, Task, Action, Result) description the candidate can use.
   </key_talking_points>

   <potential_questions>
   List 10 likely interview questions specific to this role and company, including behavioral questions, technical questions, and company-specific questions.
   </potential_questions>

   <suggested_answers>
   Provide brief but effective sample answers to the potential questions that highlight the candidate's experience.
   </suggested_answers>

   <questions_to_ask>
   Suggest 5-7 thoughtful questions the candidate should ask the interviewer that demonstrate research and genuine interest in the role and company.
   </questions_to_ask>

   <company_insights>
   Provide key insights about the company culture, recent news, challenges, or initiatives that the candidate should know before the interview.
   </company_insights>

5. Format the cheat sheet in a clear, organized manner that would be easy for the candidate to review before an interview.

Output only the completed interview prep cheat sheet with appropriate section headings and formatting. Do not include additional explanations or notes."""

    # Call Anthropic API
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=7000,
        temperature=0.7,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    }
                ]
            }
        ]
    )
    
    # Return the generated interview prep cheat sheet
    return response.content[0].text

def _extract_section(text, section_name):
    """
    Helper function to extract a section from the XML-like response
    
    Args:
        text (str): Text containing XML-like tags
        section_name (str): Name of the section to extract
        
    Returns:
        str: Content of the section
    """
    import re
    pattern = f"<{section_name}>(.*?)</{section_name}>"
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    return "Section not found in the response"