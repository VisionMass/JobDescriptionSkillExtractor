import streamlit as st
import numpy as np
import json
import PyPDF2
import fitz
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Job Description Skill Extractor",
    page_icon="💼",
    layout="wide"
)

st.title("💼 Job Description Skill Extractor")
st.markdown("Upload a job description PDF to find similar jobs and extract key skills")

# Load job vectors and metadata
@st.cache_resource
def load_data():
    """Load job vectors and metadata"""
    # Get the directory where app.py is located
    script_dir = Path(__file__).parent
    vectors_path = script_dir / "job_vectors.npy"
    metadata_path = script_dir / "job_metadata.json"
    
    if not vectors_path.exists() or not metadata_path.exists():
        st.error(f"Error: Files not found!\nLooking in: {script_dir}\nVectors: {vectors_path.exists()}\nMetadata: {metadata_path.exists()}")
        return None, None
    
    vectors = np.load(vectors_path)
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    return vectors, metadata

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

# Simple vector representation (placeholder)
def get_text_vector(text):
    """Create a simple vector representation of text"""
    from sklearn.feature_extraction.text import TfidfVectorizer
    # This is a placeholder - ideally use the same model as the backend
    vectorizer = TfidfVectorizer(max_features=100)
    vector = vectorizer.fit_transform([text]).toarray()[0]
    return vector

# Extract skills from text
def extract_skills(text):
    """Extract technical skills from text"""
    # Common technical skills and keywords
    skills_dict = {
        'Python': ['python'],
        'Java': ['java'],
        'C#': ['c#', 'c-sharp'],
        'JavaScript': ['javascript', 'js'],
        'TypeScript': ['typescript'],
        'React': ['react', 'reactjs'],
        'Vue.js': ['vue', 'vuejs'],
        'Angular': ['angular'],
        'Node.js': ['node.js', 'nodejs', 'node'],
        '.NET': ['.net', 'dot net'],
        'SQL': ['sql', 'pl/sql'],
        'MongoDB': ['mongodb', 'mongo'],
        'PostgreSQL': ['postgresql', 'postgres'],
        'MySQL': ['mysql'],
        'AWS': ['aws', 'amazon web services'],
        'Azure': ['azure', 'microsoft azure'],
        'GCP': ['gcp', 'google cloud'],
        'Docker': ['docker'],
        'Kubernetes': ['kubernetes', 'k8s'],
        'Git': ['git'],
        'CI/CD': ['ci/cd', 'continuous integration', 'continuous deployment'],
        'DevOps': ['devops'],
        'REST API': ['rest api', 'restful api', 'api'],
        'GraphQL': ['graphql'],
        'Agile': ['agile', 'scrum'],
        'Machine Learning': ['machine learning', 'ml'],
        'Data Science': ['data science'],
        'AI': ['artificial intelligence', 'ai'],
        'HTML': ['html'],
        'CSS': ['css'],
        'Bootstrap': ['bootstrap'],
        'Microservices': ['microservices'],
        'Cloud': ['cloud'],
        'Linux': ['linux'],
        'Windows': ['windows'],
        'Testing': ['testing', 'unit test', 'test automation'],
    }
    
    text_lower = text.lower()
    found_skills = set()
    
    for skill, keywords in skills_dict.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_skills.add(skill)
                break
    
    return sorted(list(found_skills))

# Find matching skills
def find_matching_skills(uploaded_skills, job_skills):
    """Find skills that match between uploaded PDF and job description"""
    matching = set(uploaded_skills) & set(job_skills)
    return sorted(list(matching))

# Main app logic
vectors, metadata = load_data()

if vectors is not None and metadata is not None:
    # Sidebar
    st.sidebar.header("📊 Database Info")
    st.sidebar.metric("Total Jobs", len(metadata))
    st.sidebar.metric("Vector Dimension", vectors.shape[1])
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload Job Description")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        
        if uploaded_file is not None:
            # Extract text from PDF
            pdf_text = extract_text_from_pdf(uploaded_file)
            
            if pdf_text:
                # Display PDF preview
                try:
                    # Convert PDF to images using PyMuPDF
                    pdf_bytes = uploaded_file.getvalue()
                    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                    num_pages = doc.page_count
                    
                    st.markdown(f"**Total Pages:** {num_pages}")
                    
                    # Show pages slider only if multiple pages
                    if num_pages > 1:
                        page_num = st.slider("Select page to view:", 1, num_pages, 1)
                    else:
                        page_num = 1
                    
                    # Render selected page
                    page = doc[page_num - 1]
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                    img_data = pix.tobytes("png")
                    st.image(img_data, caption=f"Page {page_num}/{num_pages}")
                    
                    doc.close()
                except Exception as e:
                    st.warning(f"Could not generate PDF preview: {e}")
                
                # Display extracted text
                with st.expander("📄 View extracted text"):
                    st.text_area("Extracted Text", pdf_text, height=200, disabled=True)
    
    with col2:
        st.subheader("🎯 Similar Jobs")
        
        if uploaded_file is not None and pdf_text:
            # Get vector for uploaded document
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
                
                # Combine uploaded text with metadata to get better vector
                all_texts = [pdf_text] + [job.get("Job_Description", "") for job in metadata]
                vectorizer = TfidfVectorizer(max_features=100)
                all_vectors = vectorizer.fit_transform(all_texts).toarray()
                uploaded_vector = all_vectors[0].reshape(1, -1)
                
                # Pad/truncate to match database vectors
                if uploaded_vector.shape[1] < vectors.shape[1]:
                    padding = np.zeros((1, vectors.shape[1] - uploaded_vector.shape[1]))
                    uploaded_vector = np.hstack([uploaded_vector, padding])
                else:
                    uploaded_vector = uploaded_vector[:, :vectors.shape[1]]
                
                # Calculate similarity
                similarities = cosine_similarity(uploaded_vector, vectors)[0]
                top_indices = np.argsort(similarities)[-5:][::-1]
                
                # Extract skills from uploaded PDF
                uploaded_skills = extract_skills(pdf_text)
                
                # Display results
                st.markdown("**Top 5 Similar Jobs:**")
                for rank, idx in enumerate(top_indices, 1):
                    if idx < len(metadata):
                        job = metadata[idx]
                        job_description = job.get('Job_Description', '')
                        job_skills = extract_skills(job_description)
                        matching_skills = find_matching_skills(uploaded_skills, job_skills)
                        
                        with st.container(border=True):
                            st.markdown(f"**#{rank}** - {job.get('Job_Title', 'N/A')}")
                            st.markdown(f"*{job.get('Company', 'N/A')}*")
                            
                            if matching_skills:
                                st.markdown(f"**Matching Skills:** {', '.join(matching_skills)}")
                            else:
                                st.markdown("**No matching skills found**")
                            
                            if "Job_Link" in job:
                                st.markdown(f"[View Job]({job['Job_Link']})")
                
            except Exception as e:
                st.error(f"Error processing vectors: {e}")
        else:
            st.info("Upload a PDF to see similar jobs")
    
    # Footer
    st.divider()
    st.markdown("""
    **How it works:**
    1. Upload a job description PDF
    2. The app extracts text from the PDF
    3. Compares it against the job database using vector similarity
    4. Shows the most relevant matching jobs
    """)

else:
    st.error("Unable to load job database. Please ensure job_vectors.npy and job_metadata.json are in the project directory.")
