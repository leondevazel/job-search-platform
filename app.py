import streamlit as st
from database import Database
from ai_helper import AIHelper
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Job Search Platform",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --accent: #4C7CFF;
        --accent-2: #7C6CF6;
        --accent-dim: rgba(76, 124, 255, 0.14);
        --surface: rgba(255, 255, 255, 0.035);
        --surface-hover: rgba(255, 255, 255, 0.06);
        --border: rgba(255, 255, 255, 0.09);
        --text-muted: #8992A6;
        --success: #34D399;
        --warning: #F5B942;
        --danger: #F1685E;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main { padding: 1.5rem 2rem 3rem; }

    /* ---- Headings ---- */
    h1 { font-weight: 800 !important; letter-spacing: -0.02em; margin-bottom: 0.1rem !important; }
    h2, h3 { font-weight: 700 !important; letter-spacing: -0.01em; }
    .stMarkdown p { color: var(--text-muted); }

    hr { border: none; border-top: 1px solid var(--border); margin: 1.4rem 0; }

    /* ---- Page header w/ ambient glow ---- */
    .page-header { position: relative; padding-top: 0.25rem; margin-bottom: 0.75rem; }
    .page-header::before {
        content: '';
        position: absolute;
        top: -60px; left: -60px;
        width: 320px; height: 220px;
        background: radial-gradient(circle, rgba(76, 124, 255, 0.28), transparent 70%);
        filter: blur(38px);
        z-index: -1;
        pointer-events: none;
    }
    .page-header h1 {
        background: linear-gradient(135deg, #F7F9FC 40%, #B9C6F2 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }
    .page-header .page-subtitle {
        color: var(--text-muted);
        font-size: 0.95rem;
        margin: 0.15rem 0 0;
    }

    /* ---- Sidebar ---- */
    [data-testid="stSidebar"] {
        background: #0D1017;
        border-right: 1px solid var(--border);
    }
    .brand {
        display: flex;
        align-items: center;
        gap: 11px;
        padding: 0.25rem 0 1.1rem;
    }
    .brand-mark {
        width: 3px;
        height: 28px;
        border-radius: 2px;
        background: linear-gradient(180deg, var(--accent), var(--accent-2));
        flex-shrink: 0;
        box-shadow: 0 0 12px rgba(76, 124, 255, 0.55);
    }
    .brand-name {
        font-weight: 800;
        font-size: 1.08rem;
        line-height: 1.15;
        background: linear-gradient(135deg, #FFFFFF 30%, #A9B8F0 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }
    .brand-sub { font-size: 0.68rem; color: var(--text-muted); letter-spacing: 0.08em; }

    .profile-chip {
        border: 1px solid var(--border);
        background: var(--surface);
        backdrop-filter: blur(14px);
        border-radius: 10px;
        padding: 10px 12px;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
    }
    .profile-chip.ok { border-color: rgba(52, 211, 153, 0.35); }
    .profile-chip.warn { border-color: rgba(245, 185, 66, 0.35); }
    .profile-chip .label { color: var(--text-muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; }
    .profile-chip .value { color: #F2F4F8; font-weight: 600; margin-top: 2px; }

    .sidebar-footer {
        color: var(--text-muted);
        font-size: 0.75rem;
        padding-top: 0.5rem;
    }

    /* Sidebar nav (radio -> pill list) */
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] { gap: 2px; }
    [data-testid="stSidebar"] label[data-testid="stRadioOption"] {
        padding: 9px 12px;
        border-radius: 8px;
        transition: background 0.15s ease;
        cursor: pointer;
    }
    [data-testid="stSidebar"] label[data-testid="stRadioOption"]:hover {
        background: var(--surface-hover);
    }
    [data-testid="stSidebar"] label[data-testid="stRadioOption"][data-selected="true"] {
        background: var(--accent-dim);
    }
    [data-testid="stSidebar"] label[data-testid="stRadioOption"] > div > div > div:first-child {
        display: none;
    }
    [data-testid="stSidebar"] label[data-testid="stRadioOption"] p {
        font-size: 0.9rem;
        font-weight: 500;
        color: #C6CBD9;
        margin: 0;
    }
    [data-testid="stSidebar"] label[data-testid="stRadioOption"][data-selected="true"] p {
        color: #F2F4F8;
        font-weight: 600;
    }

    /* ---- Metrics ---- */
    [data-testid="stMetric"] {
        background: var(--surface);
        backdrop-filter: blur(14px);
        border: 1px solid var(--border);
        border-top: 2px solid var(--accent);
        border-radius: 10px;
        padding: 12px 14px;
    }
    [data-testid="stMetricLabel"] p {
        color: var(--text-muted) !important;
        font-size: 0.72rem !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    [data-testid="stMetricValue"] {
        font-weight: 700 !important;
        color: #F2F4F8 !important;
    }

    /* ---- Buttons ---- */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 2.75em;
        font-weight: 600;
        border: 1px solid var(--border);
        transition: all 0.18s ease;
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent), var(--accent-2));
        border: 1px solid transparent;
        box-shadow: 0 2px 10px rgba(76, 124, 255, 0.28);
    }
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(76, 124, 255, 0.4);
    }
    .stButton>button[kind="secondary"]:hover {
        border-color: var(--accent);
        color: var(--accent);
        transform: translateY(-1px);
    }

    /* ---- Company card w/ score ring ---- */
    .company-card {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 14px 20px;
        border-radius: 14px;
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent);
        background: var(--surface);
        backdrop-filter: blur(14px);
        margin-bottom: 12px;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
    }
    .company-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.35);
        border-color: rgba(255, 255, 255, 0.18);
    }
    .company-card h3 {
        color: #F2F4F8;
        margin: 0 0 2px;
        font-size: 1.02rem;
        font-weight: 700;
    }
    .company-card .tier-label {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .score-ring {
        width: 52px;
        height: 52px;
        min-width: 52px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .score-ring-inner {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: #0C0F17;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.72rem;
        font-weight: 700;
    }

    /* ---- Expanders ---- */
    [data-testid="stExpander"] {
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        background: var(--surface);
        backdrop-filter: blur(14px);
    }
    [data-testid="stExpander"] summary { font-weight: 500; }

    /* ---- Inputs ---- */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 8px !important;
        border-color: var(--border) !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent) !important;
    }

    /* ---- Alerts ---- */
    [data-testid="stAlertContainer"] {
        border-radius: 10px !important;
        border: 1px solid var(--border) !important;
        background: var(--surface) !important;
        backdrop-filter: blur(14px);
    }
    [data-testid="stAlertContainer"] p { color: #DEE1EA !important; }
    [data-testid="stAlertContentError"] { border-left: 3px solid var(--danger); }
    [data-testid="stAlertContentWarning"] { border-left: 3px solid var(--warning); }
    [data-testid="stAlertContentSuccess"] { border-left: 3px solid var(--success); }
    [data-testid="stAlertContentInfo"] { border-left: 3px solid var(--accent); }

    /* ---- Timeline (Recent Activity) ---- */
    .timeline { position: relative; padding-left: 18px; margin-top: 4px; }
    .timeline-item { position: relative; padding-bottom: 20px; }
    .timeline-item:last-child { padding-bottom: 0; }
    .timeline-item::before {
        content: '';
        position: absolute;
        left: -18px; top: 4px;
        width: 9px; height: 9px;
        border-radius: 50%;
        background: var(--dot-color, var(--accent));
        box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.06);
    }
    .timeline-item::after {
        content: '';
        position: absolute;
        left: -14px; top: 15px; bottom: -6px;
        width: 1px;
        background: var(--border);
    }
    .timeline-item:last-child::after { display: none; }
    .timeline-item .t-title { font-weight: 600; color: #F2F4F8; font-size: 0.92rem; }
    .timeline-item .t-meta { font-size: 0.78rem; color: var(--text-muted); margin-top: 2px; }
    </style>
""", unsafe_allow_html=True)

# Initialize
if 'db' not in st.session_state:
    st.session_state.db = Database()
if 'ai' not in st.session_state:
    try:
        st.session_state.ai = AIHelper()
        st.session_state.ai_available = True
    except ValueError as e:
        st.session_state.ai_available = False
        st.error(f"Warning: {str(e)}")

db = st.session_state.db
ai = st.session_state.ai if st.session_state.ai_available else None


def page_header(title, subtitle):
    st.markdown(f"""
        <div class="page-header">
            <h1>{title}</h1>
            <p class="page-subtitle">{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
        <div class="brand">
            <span class="brand-mark"></span>
            <div>
                <div class="brand-name">Job Platform</div>
                <div class="brand-sub">CAREER INTELLIGENCE</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    profile = db.get_profile()
    if profile:
        st.markdown(f"""
            <div class="profile-chip ok">
                <div class="label">Signed in as</div>
                <div class="value">{profile.get('name', 'User')}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="profile-chip warn">
                <div class="label">Setup required</div>
                <div class="value">Complete your profile</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["Profile Setup", "Discover Jobs", "My Applications", "Analytics"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    stats = db.get_statistics()
    col1, col2 = st.columns(2)
    col1.metric("Applications", stats['total'])
    col2.metric("Interviews", stats['interview'])

    st.markdown("---")
    st.markdown('<div class="sidebar-footer">Built by Sunghoon Lee</div>', unsafe_allow_html=True)

# ===== PROFILE SETUP PAGE =====
if page == "Profile Setup":
    page_header("Profile Setup", "Set up your profile to get personalized job recommendations")
    
    current_profile = db.get_profile() or {}
    
    with st.form("profile_form"):
        st.subheader("Basic Information")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(
                "Full Name",
                value=current_profile.get('name', ''),
                placeholder="Sunghoon Lee"
            )
            education = st.text_input(
                "Education",
                value=current_profile.get('education', ''),
                placeholder="B.S. Computer Science, UW-Madison"
            )
        
        with col2:
            experience = st.selectbox(
                "Experience Level",
                ["New Graduate", "0-1 years", "1-3 years", "3-5 years", "5+ years"],
                index=["New Graduate", "0-1 years", "1-3 years", "3-5 years", "5+ years"].index(
                    current_profile.get('experience', 'New Graduate')
                )
            )
            target_location = st.text_input(
                "Target Location",
                value=current_profile.get('target_location', ''),
                placeholder="Seoul, Korea / Bay Area, USA"
            )
        
        st.markdown("---")
        st.subheader("Technical Skills")
        st.markdown("Enter your skills (comma-separated)")
        
        skills_input = st.text_area(
            "Skills",
            value=", ".join(current_profile.get('skills', [])),
            placeholder="Python, Java, React, Node.js, AWS, Machine Learning",
            height=100
        )
        
        st.markdown("---")
        st.subheader("Target Positions")
        
        col1, col2 = st.columns(2)
        with col1:
            target_roles = st.text_area(
                "Roles of Interest",
                value=", ".join(current_profile.get('target_roles', [])),
                placeholder="Software Engineer, Data Scientist, Backend Developer",
                height=100
            )
        
        with col2:
            target_companies = st.text_area(
                "Companies of Interest (Optional)",
                value=", ".join(current_profile.get('target_companies', [])),
                placeholder="Samsung, SK Hynix, Google, Naver",
                height=100
            )
        
        submitted = st.form_submit_button("Save Profile", type="primary")
        
        if submitted:
            profile_data = {
                'name': name,
                'education': education,
                'experience': experience,
                'target_location': target_location,
                'skills': [s.strip() for s in skills_input.split(',') if s.strip()],
                'target_roles': [r.strip() for r in target_roles.split(',') if r.strip()],
                'target_companies': [c.strip() for c in target_companies.split(',') if c.strip()]
            }
            
            db.save_profile(profile_data)
            st.success("Profile saved successfully")
            st.rerun()

# ===== DISCOVER JOBS PAGE =====
elif page == "Discover Jobs":
    page_header("Discover Jobs", "AI-powered job recommendations tailored to your profile")
    
    profile = db.get_profile()
    
    if not profile:
        st.warning("Complete your profile first to get personalized recommendations")
        st.info("Use the sidebar to navigate to 'Profile Setup'")
        st.stop()
    
    if not st.session_state.ai_available:
        st.error("AI features unavailable. Check API configuration.")
        st.stop()
    
    # Profile summary
    with st.expander("Your Profile Summary", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {profile.get('name', 'N/A')}")
            st.write(f"**Education:** {profile.get('education', 'N/A')}")
            st.write(f"**Experience:** {profile.get('experience', 'N/A')}")
        with col2:
            st.write(f"**Location:** {profile.get('target_location', 'N/A')}")
            st.write(f"**Skills:** {', '.join(profile.get('skills', [])[:5])}")
            if len(profile.get('skills', [])) > 5:
                st.write(f"... and {len(profile.get('skills', [])) - 5} more")
    
    st.markdown("---")
    
    # Get recommendations button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        get_recs = st.button("Get AI Recommendations", type="primary", use_container_width=True)
    
    if get_recs:
        with st.spinner("AI is analyzing your profile and finding the best matches..."):
            recommendations = ai.recommend_companies(profile)
            st.session_state.recommendations = recommendations
            st.session_state.show_count = 10
    
    # Display recommendations if they exist
    if 'recommendations' in st.session_state:
        st.markdown("---")
        st.subheader("Recommended Companies for You")
        
        # Parse recommendations
        rec_text = st.session_state.recommendations
        companies = rec_text.split('---')
        
        # Parse all companies
        all_companies = []
        for company_block in companies:
            if not company_block.strip():
                continue
            
            lines = [line.strip() for line in company_block.strip().split('\n') if line.strip()]
            
            company_info = {}
            for line in lines:
                if line.startswith('**Company:**'):
                    company_info['name'] = line.replace('**Company:**', '').strip()
                elif line.startswith('**Position:**'):
                    company_info['position'] = line.replace('**Position:**', '').strip()
                elif line.startswith('**Match Score:**'):
                    score_text = line.replace('**Match Score:**', '').strip()
                    company_info['score'] = score_text
                elif line.startswith('**Why Good Match:**'):
                    company_info['match'] = line.replace('**Why Good Match:**', '').strip()
                elif line.startswith('**Requirements:**'):
                    company_info['requirements'] = line.replace('**Requirements:**', '').strip()
                elif line.startswith('**Gaps:**'):
                    company_info['gaps'] = line.replace('**Gaps:**', '').strip()
            
            if company_info.get('name'):
                all_companies.append(company_info)
        
        # Initialize show_count if not exists
        if 'show_count' not in st.session_state:
            st.session_state.show_count = 10
        
        # Display companies up to show_count
        displayed_count = min(st.session_state.show_count, len(all_companies))
        
        for idx, company_info in enumerate(all_companies[:displayed_count]):
            
            try:
                score_num = int(company_info.get('score', '0%').replace('%', ''))
            except:
                score_num = 0

            if score_num >= 80:
                tier_color, tier_label = "var(--success)", "Strong fit"
            elif score_num >= 60:
                tier_color, tier_label = "var(--warning)", "Good fit"
            else:
                tier_color, tier_label = "var(--danger)", "Possible fit"

            ring_deg = max(0, min(score_num, 100)) * 3.6

            # Company header card with circular score ring
            st.markdown(f"""
            <div class="company-card" style="border-left-color:{tier_color};">
                <div class="score-ring" style="background: conic-gradient({tier_color} {ring_deg}deg, rgba(255,255,255,0.08) {ring_deg}deg 360deg);">
                    <div class="score-ring-inner" style="color:{tier_color};">{score_num}%</div>
                </div>
                <div class="company-card-info">
                    <h3>{company_info.get('name', 'Unknown')} &mdash; {company_info.get('position', 'N/A')}</h3>
                    <span class="tier-label" style="color:{tier_color};">{tier_label}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**Why Good Match:** {company_info.get('match', 'N/A')}")
                
                with st.expander("View Details"):
                    st.write(f"**Requirements:** {company_info.get('requirements', 'N/A')}")
                    st.write(f"**Gaps:** {company_info.get('gaps', 'N/A')}")
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("Add to Applications", key=f"add_{idx}", type="primary", use_container_width=True):
                    new_app = {
                        'company': company_info.get('name', 'Unknown'),
                        'position': company_info.get('position', 'N/A'),
                        'job_url': '',
                        'job_description': f"Match Score: {company_info.get('score')}\n\nRequirements: {company_info.get('requirements')}\n\nGaps: {company_info.get('gaps')}",
                        'status': 'Applied',
                        'keywords': f"Match: {company_info.get('match')}"
                    }
                    db.add_application(new_app)
                    st.success(f"Added {company_info.get('name')} to your applications")
            
            # Detailed Analysis Section
            with st.expander("View Detailed Analysis"):
                job_desc = st.text_area(
                    "Paste Job Description for detailed analysis",
                    height=200,
                    placeholder="Paste the actual job description here...",
                    key=f"job_desc_{idx}"
                )
                
                col_a, col_b = st.columns([1, 1])
                
                with col_a:
                    if st.button("Generate Analysis", type="primary", key=f"gen_{idx}", use_container_width=True):
                        if job_desc:
                            with st.spinner("Analyzing..."):
                                detailed_analysis = ai.analyze_company_fit(
                                    profile, 
                                    company_info.get('name'), 
                                    job_desc
                                )
                                st.session_state[f'analysis_{idx}'] = detailed_analysis
                                
                                gaps_text = company_info.get('gaps', '')
                                if gaps_text and gaps_text != 'N/A':
                                    target_skills = [s.strip() for s in gaps_text.split(',')]
                                    roadmap = ai.generate_learning_roadmap(
                                        profile.get('skills', []),
                                        target_skills
                                    )
                                    st.session_state[f'roadmap_{idx}'] = roadmap
                                st.rerun()
                        else:
                            st.warning("Please paste a job description")
                
                with col_b:
                    if st.button("Add to Applications", key=f"add_detail_{idx}", use_container_width=True):
                        new_app = {
                            'company': company_info.get('name', 'Unknown'),
                            'position': company_info.get('position', 'N/A'),
                            'job_url': '',
                            'job_description': job_desc if job_desc else f"Match Score: {company_info.get('score')}\n\nRequirements: {company_info.get('requirements')}\n\nGaps: {company_info.get('gaps')}",
                            'status': 'Applied',
                            'keywords': f"Match: {company_info.get('match')}"
                        }
                        db.add_application(new_app)
                        st.success("Added to applications")
                
                if f'analysis_{idx}' in st.session_state:
                    st.markdown("---")
                    st.markdown("#### Analysis Results")
                    st.markdown(st.session_state[f'analysis_{idx}'])
                
                if f'roadmap_{idx}' in st.session_state:
                    st.markdown("---")
                    st.markdown("#### Learning Roadmap")
                    st.markdown(st.session_state[f'roadmap_{idx}'])
            
            st.markdown("---")
        
        # Load More button
        if displayed_count < len(all_companies) and displayed_count < 30:
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("Load More (5 more)", use_container_width=True):
                    st.session_state.show_count = min(st.session_state.show_count + 5, 30)
                    st.rerun()
        
        # Show count info
        st.caption(f"Showing {displayed_count} of {min(len(all_companies), 30)} companies")

# ===== MY APPLICATIONS PAGE =====
elif page == "My Applications":
    page_header("My Applications", "Track and manage your job applications")
    
    apps = db.get_all_applications()
    stats = db.get_statistics()
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", stats['total'])
    col2.metric("Applied", stats['applied'])
    col3.metric("Interviews", stats['interview'])
    col4.metric("Offers", stats['offer'])
    
    st.markdown("---")
    
    # Add new application
    with st.expander("Add New Application"):
        with st.form("new_app"):
            col1, col2 = st.columns(2)
            
            with col1:
                company = st.text_input("Company Name", placeholder="Samsung Electronics")
                position = st.text_input("Position", placeholder="Software Engineer")
            
            with col2:
                job_url = st.text_input("Job URL", placeholder="https://...")
                status = st.selectbox("Status", ["Applied", "Interview", "Offer", "Rejected"])
            
            job_desc = st.text_area(
                "Job Description",
                height=200,
                placeholder="Paste job description"
            )
            
            col1, col2 = st.columns([3, 1])
            with col2:
                submit = st.form_submit_button("Save", type="primary", use_container_width=True)
            
            if submit:
                if company and position and job_desc:
                    keywords = None
                    if st.session_state.ai_available:
                        with st.spinner("Analyzing..."):
                            keywords = ai.extract_keywords(job_desc)
                    
                    db.add_application({
                        'company': company,
                        'position': position,
                        'job_url': job_url,
                        'job_description': job_desc,
                        'status': status,
                        'keywords': keywords
                    })
                    st.success(f"Added {company}")
                    st.rerun()
                else:
                    st.error("Fill in required fields")
    
    st.markdown("---")
    
    # Applications list
    if len(apps) == 0:
        st.info("No applications yet")
    else:
        st.subheader(f"Applications ({len(apps)})")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("Search", "")
        with col2:
            filter_status = st.selectbox("Filter", ["All", "Applied", "Interview", "Offer", "Rejected"])
        
        filtered = apps
        if search:
            filtered = [a for a in filtered if search.lower() in a.get('company', '').lower() 
                       or search.lower() in a.get('position', '').lower()]
        if filter_status != "All":
            filtered = [a for a in filtered if a.get('status') == filter_status]
        
        for app in filtered:
            with st.expander(f"{app.get('company')} - {app.get('position')} ({app.get('status')})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Applied:** {app.get('date_applied')}")
                    st.write(f"**Status:** {app.get('status')}")
                    if app.get('job_url'):
                        st.markdown(f"[Job Posting]({app['job_url']})")
                    
                    if app.get('keywords'):
                        with st.expander("AI Analysis"):
                            st.markdown(app['keywords'])
                
                with col2:
                    new_status = st.selectbox(
                        "Update",
                        ["Applied", "Interview", "Offer", "Rejected"],
                        index=["Applied", "Interview", "Offer", "Rejected"].index(app.get('status', 'Applied')),
                        key=f"s_{app['id']}"
                    )
                    
                    if st.button("Save", key=f"save_{app['id']}"):
                        db.update_application(app['id'], {'status': new_status})
                        st.success("Updated")
                        st.rerun()
                    
                    if st.button("Delete", key=f"del_{app['id']}"):
                        db.delete_application(app['id'])
                        st.success("Deleted")
                        st.rerun()

# ===== ANALYTICS PAGE =====
elif page == "Analytics":
    page_header("Analytics", "Job search insights")
    
    apps = db.get_all_applications()
    stats = db.get_statistics()
    
    if len(apps) == 0:
        st.info("No data yet")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Status Distribution")
            st.bar_chart({
                "Applied": stats['applied'],
                "Interview": stats['interview'],
                "Offer": stats['offer'],
                "Rejected": stats['rejected']
            }, color="#4C7CFF")
        
        with col2:
            st.subheader("Recent Activity")

            status_color = {
                "Applied": "var(--accent)",
                "Interview": "var(--warning)",
                "Offer": "var(--success)",
                "Rejected": "var(--danger)",
            }

            items = "".join(f"""
                <div class="timeline-item" style="--dot-color: {status_color.get(app.get('status'), 'var(--accent)')};">
                    <div class="t-title">{app['company']} &mdash; {app['position']}</div>
                    <div class="t-meta">{app['status']} on {app['date_applied']}</div>
                </div>
            """ for app in apps[:5])

            st.markdown(f'<div class="timeline">{items}</div>', unsafe_allow_html=True)