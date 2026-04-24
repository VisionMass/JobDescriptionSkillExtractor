# JobDescriptionSkillExtractor

A web application that extracts and matches skills from job descriptions using vector similarity and skill recognition.

## Features

- **PDF Upload & Preview** - Upload job description PDFs with visual preview
- **Text Extraction** - Automatically extracts text from PDF documents
- **Skill Matching** - Identifies technical skills in job descriptions (Python, React, Docker, AWS, etc.)
- **Job Matching** - Finds similar jobs from the database using vector similarity
- **Skill Comparison** - Shows which skills match between uploaded job descriptions and database jobs

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

1. **Upload** - Select a job description PDF to upload
2. **Extract** - The app extracts text and identifies skills (Python, Java, React, Docker, AWS, etc.)
3. **Match** - Compares your PDF against the job database using vector similarity
4. **Results** - Shows the top 5 matching jobs with:
   - Job title and company
   - Matching skills found in both the PDF and job description
   - Link to view the full job posting

## Supported Skills

The app recognizes technical skills including but not limited to:
- **Languages:** Python, Java, C#, JavaScript, TypeScript
- **Frameworks:** React, Vue.js, Angular, Node.js, .NET
- **Databases:** SQL, MongoDB, PostgreSQL, MySQL
- **Cloud:** AWS, Azure, GCP
- **DevOps:** Docker, Kubernetes, Git, CI/CD, Jenkins
- **Other:** REST API, GraphQL, Agile, Scrum, Machine Learning, Data Science

## Technology Stack

- **Frontend:** Streamlit
- **PDF Processing:** PyMuPDF (fitz), PyPDF2
- **ML/AI:** scikit-learn, numpy
- **Vector Similarity:** cosine_similarity

## License

MIT

## Author

Vision Mass Team