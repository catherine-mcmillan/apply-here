import logging
import re
from tqdm import tqdm

logger = logging.getLogger("apply-here.resume_generator")

def generate_updated_resume(original_resume_text, suggestions, job_description):
    """
    Generate an updated resume based on the original resume and suggestions
    
    Args:
        original_resume_text (str): Original resume text
        suggestions (dict): Suggestions for improvement
        job_description (str): Job description text
        
    Returns:
        str: Updated resume in LaTeX format
    """
    with tqdm(total=100, desc="Formatting updated resume", 
              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
        
        pbar.update(10)
        logger.info("Converting resume to LaTeX format")
        
        # Clean up the original resume text to convert to LaTeX
        # This is a simplified transformation - in a real implementation,
        # this would parse the resume structure and apply formatting rules
        
        # Split resume into sections
        resume_lines = original_resume_text.strip().split('\n')
        pbar.update(20)
        
        # Format the resume in LaTeX
        latex_resume = []
        
        # Add LaTeX document preamble
        latex_resume.append(r"""\documentclass[11pt,a4paper,sans]{moderncv}
\moderncvstyle{classic}
\moderncvcolor{blue}
\usepackage[scale=0.85]{geometry}
\usepackage{enumitem}

% Personal information
\name{}{} % Your name is auto-detected from the resume text
\begin{document}
""")
        
        current_section = None
        in_list = False
        contact_info = {}
        
        # Extract name from the first non-empty line if it looks like a name
        for line in resume_lines:
            if line.strip() and not re.search(r'@|\d{3}[-\s]?\d{3}[-\s]?\d{4}|linkedin\.com', line.lower()):
                # This is likely the name
                name_parts = line.strip().split()
                if len(name_parts) >= 2:  # Assume at least first and last name
                    first_name = name_parts[0]
                    last_name = " ".join(name_parts[1:])
                    latex_resume[0] = latex_resume[0].replace(r'\name{}{}', fr'\name{{{first_name}}}{{{last_name}}}')
                break
        
        # Process the resume line by line
        for line in resume_lines:
            clean_line = line.strip()
            
            # Skip empty lines
            if not clean_line:
                continue
            
            # Try to extract contact information
            if '@' in clean_line and 'email' not in contact_info:
                email = re.search(r'[\w\.-]+@[\w\.-]+', clean_line)
                if email:
                    contact_info['email'] = email.group(0)
            
            if re.search(r'\d{3}[-\s]?\d{3}[-\s]?\d{4}', clean_line) and 'phone' not in contact_info:
                phone = re.search(r'\d{3}[-\s]?\d{3}[-\s]?\d{4}', clean_line)
                if phone:
                    contact_info['phone'] = phone.group(0)
            
            if 'linkedin.com' in clean_line.lower() and 'linkedin' not in contact_info:
                linkedin = re.search(r'linkedin\.com/in/[\w-]+', clean_line.lower())
                if linkedin:
                    contact_info['linkedin'] = f"linkedin.com/in/{linkedin.group(0).split('/')[-1]}"
            
            # Check if this is a section header (all caps or ends with a colon)
            if clean_line.isupper() or (clean_line.endswith(':') and len(clean_line) < 40):
                # End any previous list
                if in_list:
                    latex_resume.append(r"\end{itemize}")
                    in_list = False
                
                # Format as a section header
                current_section = clean_line.strip(':').title()
                latex_resume.append(f"\n\\section{{{current_section}}}\n")
            
            # Check if this is likely a bullet point
            elif clean_line.startswith('-') or clean_line.startswith('•') or clean_line.startswith('*'):
                # Start itemize environment if not already in one
                if not in_list:
                    latex_resume.append(r"\begin{itemize}[leftmargin=*]")
                    in_list = True
                
                # Add the item, escaping LaTeX special characters
                item_text = clean_line.lstrip('-•* \t')
                item_text = escape_latex(item_text)
                latex_resume.append(f"  \\item {item_text}")
            
            # Check if this might be a job title or company name
            elif len(clean_line) < 50 and not re.search(r'\b(is|are|was|were|have|has|had|do|does|did)\b', clean_line.lower()):
                # End any previous list
                if in_list:
                    latex_resume.append(r"\end{itemize}")
                    in_list = False
                
                # Format as a subsection or cventry
                if current_section and current_section.lower() in ['experience', 'work experience', 'employment']:
                    # Try to parse company and date
                    company_match = re.search(r'^(.*?)(?:\s*\(|\s*\d{4})', clean_line)
                    date_match = re.search(r'(\d{4}\s*-\s*(?:\d{4}|present|current))', clean_line, re.IGNORECASE)
                    
                    if company_match:
                        company = company_match.group(1).strip()
                        date = date_match.group(1) if date_match else ""
                        
                        # Try to find position in nearby lines
                        position = ""
                        for i in range(resume_lines.index(line) + 1, min(resume_lines.index(line) + 4, len(resume_lines))):
                            if i < len(resume_lines) and not resume_lines[i].strip().startswith(('-', '•', '*')):
                                position_candidate = resume_lines[i].strip()
                                if position_candidate and len(position_candidate) < 50:
                                    position = position_candidate
                                    break
                        
                        # Escape LaTeX special characters
                        company = escape_latex(company)
                        position = escape_latex(position)
                        date = escape_latex(date)
                        
                        latex_resume.append(f"\\cventry{{{date}}}{{{position}}}{{{company}}}{{}}{{}}{{}}")
                    else:
                        # Just a simple subsection
                        subsection_text = escape_latex(clean_line)
                        latex_resume.append(f"\\subsection{{{subsection_text}}}")
                
                elif current_section and current_section.lower() in ['education', 'academic background']:
                    # Parse education entry
                    institution_match = re.search(r'^(.*?)(?:\s*\(|\s*\d{4})', clean_line)
                    date_match = re.search(r'(\d{4}\s*-\s*(?:\d{4}|present|current))', clean_line, re.IGNORECASE)
                    
                    if institution_match:
                        institution = institution_match.group(1).strip()
                        date = date_match.group(1) if date_match else ""
                        
                        # Try to find degree in nearby lines
                        degree = ""
                        for i in range(resume_lines.index(line) + 1, min(resume_lines.index(line) + 4, len(resume_lines))):
                            if i < len(resume_lines) and not resume_lines[i].strip().startswith(('-', '•', '*')):
                                degree_candidate = resume_lines[i].strip()
                                if degree_candidate and len(degree_candidate) < 100:
                                    degree = degree_candidate
                                    break
                        
                        # Escape LaTeX special characters
                        institution = escape_latex(institution)
                        degree = escape_latex(degree)
                        date = escape_latex(date)
                        
                        latex_resume.append(f"\\cventry{{{date}}}{{{degree}}}{{{institution}}}{{}}{{}}{{}}")
                    else:
                        # Just a simple subsection
                        subsection_text = escape_latex(clean_line)
                        latex_resume.append(f"\\subsection{{{subsection_text}}}")
                
                else:
                    # Just a simple subsection
                    subsection_text = escape_latex(clean_line)
                    latex_resume.append(f"\\subsection{{{subsection_text}}}")
            
            # Otherwise, treat as regular text if not in a list
            elif not in_list:
                # Only include if not already captured as name or contact info
                if not any(info in clean_line for info in contact_info.values()):
                    text = escape_latex(clean_line)
                    latex_resume.append(text)
        
        # End any open lists
        if in_list:
            latex_resume.append(r"\end{itemize}")
        
        pbar.update(50)
        
        # Add contact information after detecting all of it
        contact_line = ""
        if 'email' in contact_info:
            contact_line += f"\\email{{{contact_info['email']}}}\n"
        if 'phone' in contact_info:
            contact_line += f"\\phone{{{contact_info['phone']}}}\n"
        if 'linkedin' in contact_info:
            contact_line += f"\\social[linkedin]{{{contact_info['linkedin']}}}\n"
        
        # Insert contact info after the name declaration
        for i, line in enumerate(latex_resume):
            if r'\begin{document}' in line:
                latex_resume.insert(i, contact_line)
                break
        
        # Add document end
        latex_resume.append(r"\end{document}")
        
        # Join the formatted sections
        formatted_resume = "\n".join(latex_resume)
        
        pbar.update(20)
        logger.info("Successfully generated LaTeX formatted resume")
        
        return formatted_resume

def escape_latex(text):
    """
    Escape LaTeX special characters in a string
    
    Args:
        text (str): Text to escape
        
    Returns:
        str: Escaped text
    """
    # Define LaTeX special characters to escape
    latex_special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
    }
    
    # Escape each special character
    for char, replacement in latex_special_chars.items():
        text = text.replace(char, replacement)
    
    return text