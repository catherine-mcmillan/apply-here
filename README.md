# Apply Here: Resume & Cover Letter Builder

Apply Here is a comprehensive tool designed to help job seekers optimize their application materials. The application takes a user's resume, a job description URL, and a company website URL as inputs, then leverages AI to provide tailored suggestions and generate application materials.

## Features

- **Resume Analysis**: Upload your resume in various formats (PDF, DOCX, DOC, TXT, LaTeX) for analysis
- **Job Description Scraping**: Automatically extract and analyze job descriptions from URLs
- **Company Research**: Extract relevant information about the company, its products, vision, and values
- **AI-Powered Suggestions**: Get tailored suggestions to improve your resume based on the job requirements
- **Custom Cover Letter Generation**: Create a personalized cover letter highlighting your relevant qualifications
- **Interview Prep**: Generate a cheat sheet to help you prepare for interviews

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Conda (recommended for environment management)
- Anthropic API Key
- Firecrawl API Key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/apply-here.git
   cd apply-here
   ```

2. Create and activate a conda environment:
   ```
   conda create -n apply-here python=3.12
   conda activate apply-here
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key
   FIRECRAWL_API_KEY=your_firecrawl_api_key
   ```

### Running the Application

Start the Streamlit server:
```
streamlit run app.py
```

Then open your browser and navigate to `http://localhost:8501`.

## Usage

1. Upload your resume using the file uploader in the sidebar
2. Enter the URL of the job description you're applying for
3. Enter the URL of the company's website
4. Click "Generate Application Materials"
5. Review the suggestions, updated resume, cover letter, and interview prep materials
6. Download the materials you want to use

## Development

### Running Tests

```
pytest
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Powered by [Anthropic Claude](https://www.anthropic.com/) for AI-generated content
- Uses [Firecrawl API](https://docs.firecrawl.dev/) for web scraping and data extraction
- Built with [Streamlit](https://streamlit.io/) framework