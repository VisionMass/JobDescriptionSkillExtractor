# JobDescriptionSkillExtractor

A web application that extracts and matches skills from job descriptions using vector similarity and skill recognition.

## Features

- **PDF Upload & Preview** - Upload job description PDFs with visual preview
- **Text Extraction** - Automatically extracts text from PDF documents
- **Skill Matching** - Identifies technical skills in structured sections (SKILLS, TOOLS, PROJECTS, EDUCATION) using word boundary matching
- **Job Matching** - Finds similar jobs from the database using vector similarity
- **Skill Comparison** - Shows which skills match between uploaded job descriptions and database jobs
- **Analytics Dashboard** - View overall statistics: total jobs, popular skills, top matching positions
- **Upload History** - Track all uploaded resumes with timestamps and results
- **Advanced Filters** - Filter jobs by location, required skills, company, and work arrangement
- **Detailed Job Info** - Display comprehensive job details including salary, location, work arrangement, and direct links
- **Smart Skill Recommendations** - AI-powered suggestions to learn skills that appear in your top matching jobs

## Project Structure

- `job_vectors.npy` - Pre-computed vector embeddings for all jobs in the database
- `job_metadata.json` - Job metadata including titles, companies, descriptions, and links
- `app.py` - Streamlit frontend application
- `.streamlit/config.toml` - Streamlit configuration

## Setup & Installation

### Prerequisites
- Python 3.11+
- Git

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/VisionMass/JobDescriptionSkillExtractor.git
   cd JobDescriptionSkillExtractor
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   source venv/bin/activate      # macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install streamlit PyPDF2 google-genai scikit-learn numpy python-dotenv PyMuPDF
   ```

### Windows / PowerShell notes

If you install packages with pip on Windows you may see a warning like:

```
WARNING: The script streamlit.exe is installed in 'C:\Users\<YourUser>\AppData\Roaming\Python\Python313\Scripts' which is not on PATH.
```

What this means: pip placed console scripts (like `streamlit.exe`) in your user Scripts folder which isn't on your PATH. You have three simple options:

- Temporary (current PowerShell session only):

```powershell
$env:Path += ';C:\Users\<YourUser>\AppData\Roaming\Python\Python313\Scripts'
streamlit run app.py
```

- Permanent (recommended for convenience): add the Scripts folder to your user PATH. In PowerShell you can run:

```powershell
$scriptPath = 'C:\Users\<YourUser>\AppData\Roaming\Python\Python313\Scripts'
if (-not ($env:Path.Split(';') -contains $scriptPath)) {
   [Environment]::SetEnvironmentVariable('Path', $env:Path + ';' + $scriptPath, 'User')
   Write-Host "Added to user PATH. Close and reopen PowerShell to apply."
} else {
   Write-Host "Path already contains the Scripts folder."
}
```

- Alternative (no PATH changes): run Streamlit via the Python module which works regardless of PATH:

```powershell
python -m streamlit run app.py
```

Notes:
- Using a virtual environment (see step 2) is the cleanest approach — it keeps dependencies per-project and avoids touching your user PATH.
- If you prefer, add the exact Scripts path shown by pip to your Windows user PATH via Settings -> Environment Variables.

## Running the Application

```bash
python -m streamlit run app.py
```

The application will start at `http://localhost:8501`

## How It Works

1. **Upload** - Select a resume/job description PDF to upload
2. **Extract** - The app extracts text and identifies skills from structured sections (SKILLS, TOOLS, PROJECTS, EDUCATION)
3. **Analyze** - Compares your document against the job database using vector similarity and skill matching
4. **View Dashboard** - See analytics on popular skills and job statistics
5. **Filter & Browse** - Use advanced filters to narrow down jobs by location, skills, company, and work arrangement
6. **Get Recommendations** - Receive AI-powered suggestions for skills to learn to improve job matches
7. **Track History** - Review previous uploads and track your application journey
8. **Results** - Shows the top matching jobs with:
   - Job title, company, and location
   - Work arrangement type (On-site, Hybrid, Remote, Flexible)
   - Matching skills found in both documents
   - Compatibility score percentage
   - Direct link to view the full job posting

## Supported Skills

The app recognizes 40+ technical skills including but not limited to:
- **Languages:** Python, Java, C#, JavaScript, TypeScript, Go, Kotlin, Swift, Ruby, PHP, Rust
- **Frameworks & Libraries:** React, Vue.js, Angular, Node.js, .NET, Django, Flask, FastAPI, Express.js, React Native, Flutter
- **Databases:** SQL, MongoDB, PostgreSQL, MySQL, Oracle, Redis, Elasticsearch
- **Cloud & DevOps:** AWS, Azure, GCP, Docker, Kubernetes, Git, GitHub, GitLab, Jenkins, CI/CD
- **Data & AI:** Machine Learning, Data Science, TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy, Jupyter
- **Other:** REST API, GraphQL, HTML, CSS, Bootstrap, Microservices, Agile, Scrum, Testing, Tableau, Power BI

## Advanced Features

### Analytics Dashboard
- View total number of jobs in the database
- See most common required skills across all jobs
- Identify top job categories and companies

### Upload History
- Automatic tracking of all uploaded documents
- View upload timestamp and results summary
- Compare results between different resumes
- Export analysis for each upload

### Advanced Job Filters
- **By Location:** Filter jobs by specific cities or regions
- **By Skills:** Find jobs that require specific skill combinations
- **By Company:** Search for opportunities in particular companies
- **By Work Arrangement:** Filter for On-site, Hybrid, Remote, or Flexible positions

### Comprehensive Job Details
- Complete job information display:
  - Job title and company name
  - Job location and work arrangement
  - Estimated salary range (when available)
  - Matching skills percentage
  - Direct link to full job posting on JobsDB

### Smart Skill Recommendations
- AI-powered analysis of your top matching jobs
- Identify which skills appear most frequently in matching positions
- Get personalized suggestions on which skills to develop
- Learn skills that would improve your job match rate

## Smart Skill Extraction

The app uses an intelligent skill extraction system that:
- **Extracts from structured sections only** - Focuses on SKILLS, TOOLS, PROJECTS, EDUCATION, and COURSEWORK sections
- **Avoids narrative text** - Ignores casual skill mentions in "About Me" or introduction sections
- **Uses word boundary matching** - Prevents false matches (e.g., "AI" won't match "Ramathibodi")
- **Ensures accuracy** - Only recognizes official skill names, not job descriptions or story references

## Technology Stack

- **Frontend:** Streamlit
- **PDF Processing:** PyMuPDF (fitz), PyPDF2
- **ML/AI:** scikit-learn, numpy
- **Vector Similarity:** cosine_similarity
- **Data Storage:** NumPy arrays, JSON

## Usage Tips

### For Best Results:
1. **Format your resume/CV properly** - Use clear section headers like "SKILLS", "TOOLS", "PROJECTS", "EDUCATION"
2. **List skills explicitly** - Add a dedicated skills section with clear skill names (e.g., "Python", "React", not "know programming")
3. **Use standard skill names** - The app recognizes 40+ common technical skills; use official names
4. **Upload PDF format** - Ensure your document is in PDF format for accurate text extraction
5. **Review recommendations** - Check the skill recommendations to identify growth areas

### Understanding Results:
- **Matching Skills:** Only skills that appear in both your resume and job description
- **Compatibility Score:** Percentage of your skills that match the job requirements
- **Top Recommendations:** Most frequently required skills across your top 5 matching jobs

## License

MIT

## Author

Vision Mass Team