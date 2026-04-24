import streamlit as st
import numpy as np
import json
import PyPDF2
import fitz
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from io import BytesIO
import pickle
from datetime import datetime
from collections import Counter
import time

# Page configuration
st.set_page_config(
    page_title="Job Description Skill Extractor",
    page_icon="💼",
    layout="wide"
)

# Add custom CSS for animations
st.markdown("""
<style>
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }
    
    @keyframes shimmer {
        0% {
            background-position: -1000px 0;
        }
        100% {
            background-position: 1000px 0;
        }
    }
    
    .animated-title {
        animation: fadeIn 1s ease-in-out;
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .animated-subtitle {
        animation: slideInLeft 1.2s ease-in-out;
        font-size: 1.1rem;
        color: #666;
    }
    
    .job-card {
        animation: fadeIn 0.8s ease-in-out;
        transition: all 0.3s ease;
        border-radius: 10px;
        padding: 20px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .job-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    .skill-badge {
        display: inline-block;
        padding: 8px 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 4px;
        animation: fadeIn 0.6s ease-in-out;
        transition: all 0.3s ease;
    }
    
    .skill-badge:hover {
        transform: scale(1.1);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .match-score {
        animation: pulse 2s ease-in-out infinite;
        font-weight: bold;
        color: #667eea;
    }
    
    .metric-card {
        animation: slideInRight 0.8s ease-in-out;
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
    }
    
    button {
        transition: all 0.3s ease;
    }
    
    button:hover {
        transform: scale(1.05);
    }
    
    .loading-spinner {
        animation: shimmer 2s infinite;
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 1000px 100%;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        animation: fadeIn 0.8s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

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
    """Extract technical skills from text with word boundary matching for accuracy"""
    import re
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
            # Use word boundaries with regex to avoid false matches
            # \b matches word boundaries, so "ai" won't match in "email"
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
                break
    
    return sorted(list(found_skills))

# Find matching skills
def find_matching_skills(uploaded_skills, job_skills):
    """Find skills that match between uploaded PDF and job description"""
    matching = set(uploaded_skills) & set(job_skills)
    return sorted(list(matching))

# Initialize session state for history
def init_session_state():
    """Initialize session state for upload history and comparisons"""
    if 'upload_history' not in st.session_state:
        st.session_state.upload_history = []
    if 'current_upload' not in st.session_state:
        st.session_state.current_upload = None

# Save upload to history
def save_to_history(filename, text, skills, matching_jobs):
    """Save upload details to history"""
    history_item = {
        'timestamp': datetime.now(),
        'filename': filename,
        'skills_found': skills,
        'matching_jobs': matching_jobs,
        'text_preview': text[:200] + '...' if len(text) > 200 else text
    }
    st.session_state.upload_history.append(history_item)

# Get skill recommendations
def get_skill_recommendations(uploaded_skills, top_jobs_skills, metadata, top_indices, threshold=3):
    """Recommend skills to learn based on top matching jobs"""
    recommendations = Counter()
    
    for idx in top_indices[:5]:  # Top 5 matching jobs
        if idx < len(metadata):
            job = metadata[idx]
            job_skills = extract_skills(job.get('Job_Description', ''))
            missing_skills = set(job_skills) - set(uploaded_skills)
            recommendations.update(missing_skills)
    
    # Return skills that appear in multiple top jobs
    suggested = [skill for skill, count in recommendations.most_common(5) if count >= threshold]
    return suggested if suggested else list(recommendations.most_common(3))[:3]

# Get database analytics
def get_database_analytics(metadata):
    """Get analytics about the job database"""
    all_jobs_skills = []
    companies = set()
    locations = set()
    
    for job in metadata:
        all_jobs_skills.extend(extract_skills(job.get('Job_Description', '')))
        companies.add(job.get('Company', 'Unknown'))
        locations.add(job.get('Job_Location', 'Not specified'))
    
    skill_counts = Counter(all_jobs_skills)
    return {
        'total_jobs': len(metadata),
        'total_companies': len(companies),
        'total_locations': len(locations),
        'top_skills': skill_counts.most_common(10),
        'unique_skills': len(skill_counts)
    }

# Main app logic
init_session_state()
vectors, metadata = load_data()

if vectors is not None and metadata is not None:
    # Get analytics for dashboard
    analytics = get_database_analytics(metadata)
    
    # Sidebar with navigation and database info
    st.sidebar.header("📊 Dashboard")
    st.sidebar.metric("Total Jobs", analytics['total_jobs'])
    st.sidebar.metric("Companies", analytics['total_companies'])
    st.sidebar.metric("Unique Skills", analytics['unique_skills'])
    
    # Show top skills in database
    st.sidebar.subheader("🔥 Top Skills in Database")
    top_5_skills = analytics['top_skills'][:5]
    for i, (skill, count) in enumerate(top_5_skills, 1):
        st.sidebar.write(f"{i}. {skill} ({count} jobs)")
    
    # Navigation
    page = st.sidebar.radio("Navigate", ["📤 Upload & Match", "📋 History", "🎯 Advanced Search"])
    
    # ==================== PAGE 1: UPLOAD & MATCH ====================
    if page == "📤 Upload & Match":
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Upload Job Description")
            uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
            
            if uploaded_file is not None:
                # Add loading animation
                with st.spinner("Processing your PDF..."):
                    time.sleep(0.3)
                    # Extract text from PDF
                    pdf_text = extract_text_from_pdf(uploaded_file)
                
                if pdf_text:
                    st.success("PDF processed successfully!")
                    time.sleep(0.3)
                    
                    # Display PDF preview
                    try:
                        pdf_bytes = uploaded_file.getvalue()
                        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                        num_pages = doc.page_count
                        
                        st.markdown(f"**Total Pages:** {num_pages}")
                        
                        if num_pages > 1:
                            page_num = st.slider("Select page to view:", 1, num_pages, 1)
                        else:
                            page_num = 1
                        
                        page_obj = doc[page_num - 1]
                        pix = page_obj.get_pixmap(matrix=fitz.Matrix(2, 2))
                        img_data = pix.tobytes("png")
                        st.image(img_data, caption=f"Page {page_num}/{num_pages}")
                        
                        doc.close()
                    except Exception as e:
                        st.warning(f"Could not generate PDF preview: {e}")
                    
                    # Display extracted text
                    with st.expander("View extracted text"):
                        st.text_area("Extracted Text", pdf_text, height=200, disabled=True)
                    
                    # Extract skills from uploaded PDF
                    with st.spinner("Extracting skills..."):
                        time.sleep(0.2)
                        uploaded_skills = extract_skills(pdf_text)
                    
                    st.session_state.current_upload = {
                        'filename': uploaded_file.name,
                        'text': pdf_text,
                        'skills': uploaded_skills
                    }
        
        with col2:
            st.subheader("Matching Results")
            
            if uploaded_file is not None and pdf_text:
                try:
                    from sklearn.feature_extraction.text import TfidfVectorizer
                    
                    # Add progress indicator
                    with st.spinner("Finding matching jobs..."):
                        time.sleep(0.3)
                        # Get vector for uploaded document
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
                        top_indices = np.argsort(similarities)[-10:][::-1]
                    
                    st.success("Analysis complete!")
                    time.sleep(0.2)

                    # Show extracted skills with animation
                    if uploaded_skills:
                        st.markdown(f"**Found Skills:** {', '.join(uploaded_skills)}")
                    else:
                        st.markdown("**No specific skills found in document**")
                    
                    st.markdown("---")
                    
                    # FEATURE 7: Enhanced Job Details with Location, Salary, etc.
                    st.markdown("**Top 10 Recommended Jobs:**")
                    
                    # Add state for showing more jobs
                    if 'show_more_jobs' not in st.session_state:
                        st.session_state.show_more_jobs = False
                    
                    # Calculate match percentages for all jobs and sort by percentage
                    jobs_with_scores = []
                    for idx in top_indices:
                        if idx < len(metadata):
                            job = metadata[idx]
                            job_description = job.get('Job_Description', '')
                            job_skills = extract_skills(job_description)
                            matching_skills = find_matching_skills(uploaded_skills, job_skills)
                            match_percentage = (len(matching_skills) / max(len(job_skills), 1)) * 100
                            jobs_with_scores.append((idx, match_percentage, matching_skills, job_skills))
                    
                    # Sort by match percentage in descending order
                    jobs_with_scores.sort(key=lambda x: x[1], reverse=True)
                    
                    # Determine how many jobs to display
                    num_jobs_to_show = len(jobs_with_scores) if st.session_state.show_more_jobs else 5
                    
                    # Animate job display with staggered effect
                    for rank, (idx, match_percentage, matching_skills, job_skills) in enumerate(jobs_with_scores[:num_jobs_to_show], 1):
                        if idx < len(metadata):
                            job = metadata[idx]
                            
                            with st.container(border=True):
                                col_title, col_score = st.columns([3, 1])
                                with col_title:
                                    st.markdown(f"**#{rank}** - {job.get('Job_Title', 'N/A')}")
                                with col_score:
                                    # Animated match score
                                    st.markdown(f"<div class='match-score'>Match: {match_percentage:.0f}%</div>", unsafe_allow_html=True)
                                
                                st.markdown(f"*{job.get('Company', 'N/A')}*")
                                
                                # FEATURE 7: Show location, work arrangement
                                col_loc, col_arrange = st.columns(2)
                                with col_loc:
                                    if job.get('Job_Location'):
                                        st.caption(f"Location: {job.get('Job_Location')}")
                                with col_arrange:
                                    if job.get('Work_Arrangement'):
                                        st.caption(f"Work: {job.get('Work_Arrangement')}")
                                
                                # Display matching skills as animated badges
                                if matching_skills:
                                    skills_html = " ".join([f"<span class='skill-badge'>{skill}</span>" for skill in matching_skills])
                                    st.markdown(f"**Matching Skills:** {skills_html}", unsafe_allow_html=True)
                                else:
                                    st.markdown("**No matching skills found**")
                                
                                # Show required skills not in resume
                                missing = set(job_skills) - set(uploaded_skills)
                                if missing:
                                    st.markdown(f"**Skills to Learn:** {', '.join(list(missing)[:3])}")
                                
                                if "Job_Link" in job:
                                    st.markdown(f"[View Full Job Post]({job['Job_Link']})")
                    
                    # Add View More button if there are more than 5 jobs
                    if len(jobs_with_scores) > 5:
                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col2:
                            if not st.session_state.show_more_jobs:
                                if st.button("View More Jobs", key="view_more_btn", use_container_width=True):
                                    st.session_state.show_more_jobs = True
                                    st.rerun()
                            else:
                                if st.button("Show Less", key="show_less_btn", use_container_width=True):
                                    st.session_state.show_more_jobs = False
                                    st.rerun()
                        
                        if st.session_state.show_more_jobs:
                            st.info(f"Showing all {len(jobs_with_scores)} matching jobs")
                    
                    # FEATURE 9: Smart Recommendations
                    st.markdown("---")
                    st.subheader("Skill Recommendations")
                    recommended = get_skill_recommendations(uploaded_skills, [], metadata, top_indices)
                    if recommended:
                        st.markdown("**To increase match rate with top jobs, consider learning:**")
                        for skill in recommended:
                            st.write(f"• **{skill}**")
                    
                    # Save to history
                    matching_jobs_info = []
                    for rank, idx in enumerate(top_indices[:5], 1):
                        if idx < len(metadata):
                            matching_jobs_info.append({
                                'rank': rank,
                                'title': metadata[idx].get('Job_Title'),
                                'company': metadata[idx].get('Company')
                            })
                    save_to_history(uploaded_file.name, pdf_text, uploaded_skills, matching_jobs_info)
                    
                except Exception as e:
                    st.error(f"Error processing vectors: {e}")
            else:
                st.info("Upload a PDF to see matching jobs")
    
    # ==================== PAGE 2: HISTORY & COMPARISON ====================
    elif page == "📋 History":
        st.subheader("📋 Upload History")
        
        if st.session_state.upload_history:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🗑️ Clear History"):
                    st.session_state.upload_history = []
                    st.rerun()
            
            # Display history as tabs for each upload
            if len(st.session_state.upload_history) > 0:
                for i, item in enumerate(reversed(st.session_state.upload_history)):
                    with st.expander(f"📄 {item['filename']} - {item['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                        col_skills, col_jobs = st.columns(2)
                        
                        with col_skills:
                            st.markdown("**Skills Found:**")
                            if item['skills_found']:
                                st.write(', '.join(item['skills_found']))
                            else:
                                st.write("No skills found")
                        
                        with col_jobs:
                            st.markdown("**Top Matching Jobs:**")
                            for job in item['matching_jobs'][:3]:
                                st.write(f"• {job['title']} ({job['company']})")
                        
                        st.markdown("**Preview:**")
                        st.caption(item['text_preview'])
        else:
            st.info("📭 No upload history yet. Upload a PDF to get started!")
    
    # ==================== PAGE 3: ADVANCED SEARCH ====================
    elif page == "🎯 Advanced Search":
        st.subheader("🎯 Advanced Job Search & Filters")
        
        # FEATURE 5: Filter options
        filter_col1, filter_col2 = st.columns(2)
        
        with filter_col1:
            selected_skills = st.multiselect(
                "Filter by Skills",
                sorted(set([skill for job in metadata for skill in extract_skills(job.get('Job_Description', ''))])),
                help="Select one or more skills to find jobs"
            )
            
            selected_location = st.multiselect(
                "Filter by Location",
                sorted(set([job.get('Job_Location', 'Not specified') for job in metadata])),
                help="Select job locations"
            )
        
        with filter_col2:
            selected_company = st.multiselect(
                "Filter by Company",
                sorted(set([job.get('Company', 'Unknown') for job in metadata]))[:20],
                help="Top 20 companies hiring"
            )
            
            selected_arrangement = st.multiselect(
                "Filter by Work Arrangement",
                sorted(set([job.get('Work_Arrangement', 'Not specified') for job in metadata])),
                help="E.g., Office, Hybrid, Remote"
            )
        
        # Apply filters
        filtered_jobs = metadata.copy()
        
        if selected_skills:
            filtered_jobs = [
                job for job in filtered_jobs 
                if any(skill in extract_skills(job.get('Job_Description', '')) for skill in selected_skills)
            ]
        
        if selected_location:
            filtered_jobs = [
                job for job in filtered_jobs 
                if job.get('Job_Location') in selected_location
            ]
        
        if selected_company:
            filtered_jobs = [
                job for job in filtered_jobs 
                if job.get('Company') in selected_company
            ]
        
        if selected_arrangement:
            filtered_jobs = [
                job for job in filtered_jobs 
                if job.get('Work_Arrangement') in selected_arrangement
            ]
        
        st.markdown(f"**Found {len(filtered_jobs)} matching jobs**")
        
        if filtered_jobs:
            # Display filtered results
            for job in filtered_jobs[:20]:  # Show top 20
                job_skills = extract_skills(job.get('Job_Description', ''))
                
                with st.container(border=True):
                    col_title, col_skills_count = st.columns([3, 1])
                    with col_title:
                        st.markdown(f"**{job.get('Job_Title', 'N/A')}**")
                    with col_skills_count:
                        st.caption(f"Skills: {len(job_skills)}")
                    
                    st.markdown(f"*{job.get('Company', 'N/A')}*")
                    
                    col_loc, col_arrange = st.columns(2)
                    with col_loc:
                        if job.get('Job_Location'):
                            st.caption(f"📍 {job.get('Job_Location')}")
                    with col_arrange:
                        if job.get('Work_Arrangement'):
                            st.caption(f"🏢 {job.get('Work_Arrangement')}")
                    
                    if job_skills:
                        st.markdown(f"**Skills Required:** {', '.join(job_skills[:5])}")
                    
                    if "Job_Link" in job:
                        st.markdown(f"[🔗 View Full Job Post]({job['Job_Link']})")
        else:
            st.warning("No jobs match your filters. Try adjusting your selections.")
    
    # Footer
    st.divider()
    st.markdown("""
    **How it works:**
    1. **Upload & Match** - Upload your resume to find similar jobs
    2. **History** - View your previous uploads and comparisons
    3. **Advanced Search** - Filter jobs by skills, location, company, and work arrangement
    4. **Smart Recommendations** - Get skill suggestions to improve your match rate
    """)

else:
    st.error("Unable to load job database. Please ensure job_vectors.npy and job_metadata.json are in the project directory.")
