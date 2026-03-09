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
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
    }
    .company-card {
        padding: 15px 20px;
        border-radius: 10px;
        border: 2px solid #3b82f6;
        margin-bottom: 15px;
        background: #1a1a1a;
        display: inline-block;
        width: auto;
        max-width: fit-content;
    }
    .company-card h3 {
        color: #ffffff;
        margin: 0;
        white-space: nowrap;
    }
    .match-score-high {
        color: #10b981;
        font-weight: bold;
        font-size: 1.2em;
    }
    .match-score-medium {
        color: #f59e0b;
        font-weight: bold;
        font-size: 1.2em;
    }
    .match-score-low {
        color: #ef4444;
        font-weight: bold;
        font-size: 1.2em;
    }
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

# Sidebar
with st.sidebar:
    st.title("AI Job Platform")
    
    profile = db.get_profile()
    if profile:
        st.success(f"Profile: {profile.get('name', 'User')}")
    else:
        st.warning("Complete your profile first")
    
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["Profile Setup", "Discover Jobs", "My Applications", "Analytics"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    stats = db.get_statistics()
    st.metric("Total Applications", stats['total'])
    st.metric("Active Interviews", stats['interview'])
    
    st.markdown("---")
    st.markdown("Built by Sunghoon Lee")

# ===== PROFILE SETUP PAGE =====
if page == "Profile Setup":
    st.title("Profile Setup")
    st.markdown("Set up your profile to get personalized job recommendations")
    
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
    st.title("Discover Jobs")
    st.markdown("AI-powered job recommendations tailored to your profile")
    
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
                if score_num >= 80:
                    score_class = "match-score-high"
                elif score_num >= 60:
                    score_class = "match-score-medium"
                else:
                    score_class = "match-score-low"
            except:
                score_class = "match-score-medium"
            
            # Company name card - inline block with auto width
            st.markdown(f"""
            <div class="company-card">
                <h3>{company_info.get('name', 'Unknown')} - {company_info.get('position', 'N/A')}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Match Score:** <span class='{score_class}'>{company_info.get('score', 'N/A')}</span>", unsafe_allow_html=True)
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
                    st.balloons()
            
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
    st.title("My Applications")
    st.markdown("Track and manage your job applications")
    
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
    st.title("Analytics")
    st.markdown("Job search insights")
    
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
            })
        
        with col2:
            st.subheader("Recent Activity")
            for app in apps[:5]:
                st.write(f"**{app['company']}** - {app['position']}")
                st.caption(f"{app['status']} on {app['date_applied']}")
                st.markdown("---")