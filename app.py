import os
import streamlit as st
import streamlit_authenticator as stauth
import altair as alt
import pandas as pd
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

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if st.session_state.dark_mode:
    palette = {
        "bg": "#000000",
        "accent": "#0A84FF",
        "accent-rgb": "10, 132, 255",
        "accent-hover": "#409CFF",
        "accent-tint": "rgba(10, 132, 255, 0.16)",
        "accent-text": "#5CACFF",
        "surface": "#1C1C1E",
        "surface-hover": "#2C2C2E",
        "hover-tint": "rgba(255, 255, 255, 0.06)",
        "border": "#38383A",
        "text": "#F5F5F7",
        "text-muted": "#98989D",
        "success": "#32D74B",
        "warning": "#FF9F0A",
        "danger": "#FF453A",
    }
else:
    palette = {
        "bg": "#FFFFFF",
        "accent": "#0071E3",
        "accent-rgb": "0, 113, 227",
        "accent-hover": "#0077ED",
        "accent-tint": "rgba(0, 113, 227, 0.08)",
        "accent-text": "#0058B0",
        "surface": "#FFFFFF",
        "surface-hover": "#F5F5F7",
        "hover-tint": "rgba(0, 0, 0, 0.04)",
        "border": "#D2D2D7",
        "text": "#1D1D1F",
        "text-muted": "#6E6E73",
        "success": "#1D8A3D",
        "warning": "#B3610A",
        "danger": "#D70015",
    }

# Custom CSS
st.markdown(f"""
    <style>
    :root {{
        --accent: {palette['accent']};
        --accent-rgb: {palette['accent-rgb']};
        --accent-hover: {palette['accent-hover']};
        --accent-tint: {palette['accent-tint']};
        --accent-text: {palette['accent-text']};
        --bg: {palette['bg']};
        --surface: {palette['surface']};
        --surface-hover: {palette['surface-hover']};
        --hover-tint: {palette['hover-tint']};
        --border: {palette['border']};
        --text: {palette['text']};
        --text-muted: {palette['text-muted']};
        --success: {palette['success']};
        --warning: {palette['warning']};
        --danger: {palette['danger']};
    }}

    html, body, [class*="css"] {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: var(--text);
    }}

    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stHeader"],
    [data-testid="stBottomBlockContainer"] {{
        background: var(--bg) !important;
    }}

    .main {{ padding: 2rem 3rem 4rem; }}
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* ---- Motion ---- */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.001ms !important;
            animation-delay: 0ms !important;
            transition-duration: 0.001ms !important;
        }
    }

    /* Smooth light/dark theme swap instead of a hard cut */
    body,
    [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"],
    [data-testid="stSidebar"], [data-testid="stMetric"], [data-testid="stExpander"],
    [data-testid="stExpanderDetails"], [data-testid="stAlertContainer"],
    .stTextInput input, .stTextArea textarea, .stSelectbox input, .stSelectbox [role="group"],
    .stButton>button, .company-card, .profile-chip, hr {
        transition: background-color 0.35s ease, border-color 0.35s ease, color 0.35s ease;
    }

    /* ---- Headings ---- */
    h1 { font-weight: 600 !important; letter-spacing: -0.03em; color: var(--text) !important; }
    h2, h3 { font-weight: 600 !important; letter-spacing: -0.02em; color: var(--text) !important; }
    .stMarkdown p { color: var(--text-muted); }
    .section-heading { font-size: 1.5rem; margin: 0.2rem 0 0.6rem; }

    hr { border: none; border-top: 1px solid var(--border); margin: 2rem 0; }

    /* ---- Page header ---- */
    .page-header {
        padding-top: 0.25rem;
        margin-bottom: 0.5rem;
        opacity: 0;
        animation: fadeInUp 0.45s ease-out forwards;
    }
    .page-header h1 { font-size: 2.4rem; margin: 0; }
    .page-header .page-subtitle {
        color: var(--text-muted);
        font-size: 1.05rem;
        margin: 0.35rem 0 0;
    }

    /* ---- Sidebar ---- */
    [data-testid="stSidebar"] {
        background: var(--surface-hover);
        border-right: 1px solid var(--border);
    }
    .brand {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0.25rem 0 1.1rem;
    }
    .brand-mark {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--accent);
        flex-shrink: 0;
    }
    .brand-name {
        font-weight: 600;
        font-size: 1.05rem;
        line-height: 1.15;
        color: var(--text);
    }
    .brand-sub { font-size: 0.68rem; color: var(--text-muted); letter-spacing: 0.06em; }

    .profile-chip {
        border: 1px solid var(--border);
        background: var(--surface);
        border-radius: 12px;
        padding: 10px 12px;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
    }
    .profile-chip .label { color: var(--text-muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em; }
    .profile-chip .value { color: var(--text); font-weight: 600; margin-top: 2px; }

    .sidebar-footer {
        color: var(--text-muted);
        font-size: 0.75rem;
        padding-top: 0.5rem;
    }

    /* Sidebar nav (radio -> pill list) */
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] { gap: 2px; }
    [data-testid="stSidebar"] label[data-testid="stRadioOption"] {
        padding: 8px 12px;
        border-radius: 8px;
        transition: background 0.15s ease, padding-left 0.15s ease;
        cursor: pointer;
    }
    [data-testid="stSidebar"] label[data-testid="stRadioOption"]:hover {
        background: var(--hover-tint);
        padding-left: 16px;
    }
    [data-testid="stSidebar"] label[data-testid="stRadioOption"][data-selected="true"] {
        background: var(--accent-tint);
    }
    [data-testid="stSidebar"] label[data-testid="stRadioOption"] > div > div > div:first-child {
        display: none;
    }
    [data-testid="stSidebar"] label[data-testid="stRadioOption"] p {
        font-size: 0.92rem;
        font-weight: 400;
        color: var(--text);
        margin: 0;
    }
    [data-testid="stSidebar"] label[data-testid="stRadioOption"][data-selected="true"] p {
        color: var(--accent-text);
        font-weight: 600;
    }

    /* ---- Metrics ---- */
    [data-testid="stMetric"] {
        background: transparent;
        padding: 0;
    }
    [data-testid="stMetricLabel"] p {
        color: var(--text-muted) !important;
        font-size: 0.78rem !important;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    [data-testid="stMetricValue"] {
        font-weight: 600 !important;
        color: var(--text) !important;
        font-size: 2rem !important;
    }

    /* ---- Buttons ---- */
    .stButton>button {
        width: 100%;
        border-radius: 980px;
        height: 2.7em;
        font-weight: 400;
        font-size: 0.95rem;
        border: 1px solid var(--border);
        background: var(--surface);
        color: var(--text);
        transition: all 0.15s ease;
    }
    .stButton>button:hover {
        border-color: var(--text-muted);
        background: var(--surface-hover);
    }
    .stButton>button:active { transform: scale(0.97); }
    .stButton>button[kind="primary"] {
        background: var(--accent);
        border: 1px solid var(--accent);
        color: #FFFFFF;
    }
    .stButton>button[kind="primary"]:hover {
        background: var(--accent-hover);
        border-color: var(--accent-hover);
    }
    /* Gentle attention pulse on the primary AI-recommendation CTA only */
    .st-key-get_recs_btn .stButton>button[kind="primary"] {
        animation: ctaPulse 2.6s ease-in-out infinite;
    }
    .st-key-get_recs_btn .stButton>button[kind="primary"]:hover { animation: none; }
    @keyframes ctaPulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(var(--accent-rgb), 0.35); }
        50% { box-shadow: 0 0 0 8px rgba(var(--accent-rgb), 0); }
    }

    /* Spinner */
    .stSpinner > div { border-top-color: var(--accent) !important; }
    .stSpinner p { color: var(--text-muted) !important; }

    /* ---- AI loading indicator ---- */
    .ai-loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 2rem 0 1.25rem;
        gap: 1.1rem;
    }
    .ai-orbit { position: relative; width: 64px; height: 64px; }
    .ai-core {
        position: absolute;
        inset: 24px;
        background: var(--accent);
        clip-path: polygon(50% 0%, 61% 39%, 100% 50%, 61% 61%, 50% 100%, 39% 61%, 0% 50%, 39% 39%);
        animation: aiCorePulse 1.6s ease-in-out infinite;
    }
    @keyframes aiCorePulse {
        0%, 100% { transform: scale(0.8) rotate(0deg); opacity: 0.75; }
        50% { transform: scale(1.05) rotate(45deg); opacity: 1; }
    }
    .ai-dot {
        position: absolute;
        top: 50%; left: 50%;
        width: 7px; height: 7px;
        margin: -3.5px;
        border-radius: 50%;
        animation: aiOrbit 2.4s linear infinite;
        animation-delay: var(--delay, 0s);
    }
    @keyframes aiOrbit {
        from { transform: rotate(0deg) translateX(29px) rotate(0deg); }
        to { transform: rotate(360deg) translateX(29px) rotate(-360deg); }
    }
    .ai-phrases { position: relative; height: 1.4em; min-width: 260px; text-align: center; }
    .ai-phrase {
        position: absolute; inset: 0;
        color: var(--text-muted);
        font-size: 0.92rem;
        opacity: 0;
        animation: aiPhraseCycle 6.4s ease-in-out infinite;
        animation-delay: var(--d, 0s);
    }
    @keyframes aiPhraseCycle {
        0% { opacity: 0; transform: translateY(5px); }
        6%, 22% { opacity: 1; transform: translateY(0); }
        28%, 100% { opacity: 0; transform: translateY(-5px); }
    }
    .ai-skeletons { width: 100%; max-width: 480px; margin-top: 0.5rem; }
    .skel-card {
        height: 62px;
        border-radius: 12px;
        margin-bottom: 10px;
        background: linear-gradient(90deg, var(--surface-hover) 25%, var(--border) 37%, var(--surface-hover) 63%);
        background-size: 400% 100%;
        animation: skelShimmer 1.5s ease infinite;
    }
    @keyframes skelShimmer {
        0% { background-position: 100% 0; }
        100% { background-position: 0 0; }
    }

    /* ---- Success checkmark ---- */
    .success-check {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 14px;
        border-radius: 10px;
        background: color-mix(in srgb, var(--success) 12%, transparent);
        border: 1px solid var(--border);
        animation: fadeInUp 0.3s ease-out;
        margin-bottom: 0.5rem;
    }
    .success-check span { color: var(--text); font-size: 0.92rem; }
    .success-check .check-circle {
        fill: none; stroke: var(--success); stroke-width: 2;
        stroke-dasharray: 63; stroke-dashoffset: 63;
        animation: checkDraw 0.4s ease-out forwards;
    }
    .success-check .check-mark {
        fill: none; stroke: var(--success); stroke-width: 2.5;
        stroke-linecap: round; stroke-linejoin: round;
        stroke-dasharray: 20; stroke-dashoffset: 20;
        animation: checkDraw 0.25s ease-out 0.35s forwards;
    }
    @keyframes checkDraw { to { stroke-dashoffset: 0; } }

    /* ---- Company card w/ score ring ---- */
    .company-card {
        display: flex;
        align-items: center;
        gap: 18px;
        padding: 18px 10px;
        border: none;
        border-bottom: 1px solid var(--border);
        border-radius: 10px;
        background: transparent;
        margin-bottom: 4px;
        opacity: 0;
        animation: fadeInUp 0.5s ease-out forwards;
        animation-delay: calc(var(--i, 0) * 70ms + 60ms);
        transition: background 0.2s ease;
    }
    .company-card:hover { background: var(--surface-hover); }
    .company-card h3 {
        color: var(--text);
        margin: 0 0 2px;
        font-size: 1.08rem;
        font-weight: 600;
        letter-spacing: -0.01em;
    }
    .company-card .tier-label {
        font-size: 0.78rem;
        font-weight: 500;
    }
    .score-ring {
        position: relative;
        width: 54px;
        height: 54px;
        min-width: 54px;
    }
    .score-ring svg { transform: rotate(-90deg); overflow: visible; }
    .ring-track { fill: none; stroke: var(--border); stroke-width: 4; }
    .ring-progress {
        fill: none;
        stroke-width: 4;
        stroke-linecap: round;
        animation: ringFill 1s cubic-bezier(0.22, 1, 0.36, 1) forwards;
        animation-delay: calc(var(--i, 0) * 70ms + 200ms);
    }
    @keyframes ringFill { from { stroke-dashoffset: 150.8; } }
    @property --num {
        syntax: '<integer>';
        inherits: false;
        initial-value: 0;
    }
    .score-ring-inner {
        position: absolute;
        inset: 6px;
        border-radius: 50%;
        background: var(--bg);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.78rem;
        font-weight: 600;
        --num: 0;
        counter-reset: sn var(--num);
        animation: scoreCountUp 1s cubic-bezier(0.22, 1, 0.36, 1) forwards;
        animation-delay: calc(var(--i, 0) * 70ms + 200ms);
    }
    .score-ring-inner::after { content: counter(sn) '%'; }
    @keyframes scoreCountUp { to { --num: var(--target-score, 0); } }

    /* ---- Expanders ---- */
    [data-testid="stExpander"] {
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        background: var(--surface);
    }
    [data-testid="stExpander"] summary {
        font-weight: 400;
        background: var(--surface) !important;
        color: var(--text) !important;
    }
    [data-testid="stExpander"] summary span[data-testid="stIconMaterial"] {
        color: var(--text-muted) !important;
    }
    [data-testid="stExpanderDetails"] { background: var(--surface) !important; }

    /* ---- Inputs ---- */
    .stTextInput input, .stTextArea textarea, .stNumberInput input,
    .stSelectbox input, .stSelectbox [role="group"] {
        border-radius: 10px !important;
        border-color: var(--border) !important;
        background: var(--surface-hover) !important;
        color: var(--text) !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-tint) !important;
    }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: var(--text-muted) !important;
        opacity: 1;
    }
    .stSelectbox button { color: var(--text) !important; }

    /* Selectbox dropdown popover (portalled to body) */
    [role="listbox"] {
        background: var(--surface-hover) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
    }
    [role="option"] { color: var(--text) !important; }
    [role="option"][aria-selected="true"], [role="option"][data-focused="true"] {
        background: var(--accent-tint) !important;
    }

    /* ---- Alerts ---- */
    [data-testid="stAlertContainer"] {
        border-radius: 10px !important;
        border: 1px solid var(--border) !important;
        background: var(--surface-hover) !important;
    }
    [data-testid="stAlertContainer"] p { color: var(--text) !important; }
    [data-testid="stAlertContentError"] { border-left: 3px solid var(--danger); }
    [data-testid="stAlertContentWarning"] { border-left: 3px solid var(--warning); }
    [data-testid="stAlertContentSuccess"] { border-left: 3px solid var(--success); }
    [data-testid="stAlertContentInfo"] { border-left: 3px solid var(--accent); }

    /* ---- Timeline (Recent Activity) ---- */
    .timeline { position: relative; padding-left: 18px; margin-top: 4px; }
    .timeline-item {
        position: relative;
        padding-bottom: 20px;
        opacity: 0;
        animation: fadeInUp 0.45s ease-out forwards;
        animation-delay: calc(var(--i, 0) * 80ms + 100ms);
    }
    .timeline-item:last-child { padding-bottom: 0; }
    .timeline-item::before {
        content: '';
        position: absolute;
        left: -18px; top: 4px;
        width: 8px; height: 8px;
        border-radius: 50%;
        background: var(--dot-color, var(--accent));
    }
    .timeline-item::after {
        content: '';
        position: absolute;
        left: -14px; top: 14px; bottom: -6px;
        width: 1px;
        background: var(--border);
    }
    .timeline-item:last-child::after { display: none; }
    .timeline-item .t-title { font-weight: 500; color: var(--text); font-size: 0.94rem; }
    .timeline-item .t-meta { font-size: 0.8rem; color: var(--text-muted); margin-top: 2px; }
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


def section_heading(text):
    # h2, not st.subheader's h3 — keeps h1 > h2 > h3 sequential for a11y
    st.markdown(f'<h2 class="section-heading">{text}</h2>', unsafe_allow_html=True)


def show_ai_loading(phrases, show_skeleton=True):
    """Render a themed AI-analysis loader and return its placeholder so the
    caller can clear it once the (blocking) AI call returns."""
    placeholder = st.empty()
    phrase_html = "".join(
        f'<span class="ai-phrase" style="--d:{i * 1.6}s">{p}</span>'
        for i, p in enumerate(phrases)
    )
    skeleton_html = (
        '<div class="ai-skeletons">'
        + '<div class="skel-card"></div>' * 3
        + '</div>'
    ) if show_skeleton else ''
    placeholder.markdown(f"""
        <div class="ai-loading">
            <div class="ai-orbit">
                <div class="ai-core"></div>
                <div class="ai-dot" style="--delay:0s; background:var(--accent);"></div>
                <div class="ai-dot" style="--delay:-0.8s; background:var(--success);"></div>
                <div class="ai-dot" style="--delay:-1.6s; background:var(--warning);"></div>
            </div>
            <div class="ai-phrases">{phrase_html}</div>
            {skeleton_html}
        </div>
    """, unsafe_allow_html=True)
    return placeholder


def success_check(message):
    st.markdown(f"""
        <div class="success-check">
            <svg viewBox="0 0 24 24" width="20" height="20">
                <circle cx="12" cy="12" r="10" class="check-circle" />
                <path d="M7 12.5l3 3 7-7" class="check-mark" />
            </svg>
            <span>{message}</span>
        </div>
    """, unsafe_allow_html=True)

# ===== AUTH GATE =====
credentials = {'usernames': db.get_all_users()}
cookie_key = os.getenv("AUTH_COOKIE_KEY", "dev-only-insecure-key-set-AUTH_COOKIE_KEY-in-production")
authenticator = stauth.Authenticate(credentials, "job_platform_auth", cookie_key, 30)

authenticator.login(location='unrendered')
auth_status = st.session_state.get("authentication_status")

if not auth_status:
    page_header("Job Platform", "Sign in to track applications, get AI-matched recommendations, and build your portfolio")

    authenticator.login(clear_on_submit=True)
    auth_status = st.session_state.get("authentication_status")
    if auth_status is False:
        st.error("Username or password is incorrect")

    with st.expander("New here? Create an account"):
        try:
            email, new_username, name = authenticator.register_user(captcha=False)
            if email:
                db.create_user(new_username, credentials['usernames'][new_username])
                success_check(f"Account created for {name} — log in above")
        except Exception as e:
            st.error(str(e))

    st.stop()

user_id = st.session_state["username"]

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

    profile = db.get_profile(user_id)
    if profile:
        st.markdown(f"""
            <div class="profile-chip">
                <div class="label">Signed in as</div>
                <div class="value">{profile.get('name', 'User')}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="profile-chip">
                <div class="label">Setup required</div>
                <div class="value">Complete your profile</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["Profile Setup", "Discover Jobs", "My Applications", "Portfolio", "Analytics"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    stats = db.get_statistics(user_id)
    col1, col2 = st.columns(2)
    col1.metric("Applications", stats['total'])
    col2.metric("Interviews", stats['interview'])

    st.markdown("---")
    st.toggle("Dark Mode", key="dark_mode")
    authenticator.logout("Log Out", "sidebar", use_container_width=True)

    st.markdown('<div class="sidebar-footer">Built by Sunghoon Lee</div>', unsafe_allow_html=True)

# ===== PROFILE SETUP PAGE =====
if page == "Profile Setup":
    page_header("Profile Setup", "Set up your profile to get personalized job recommendations")
    
    current_profile = db.get_profile(user_id) or {}
    
    with st.form("profile_form"):
        section_heading("Basic Information")
        
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
        section_heading("Technical Skills")
        st.markdown("Enter your skills (comma-separated)")
        
        skills_input = st.text_area(
            "Skills",
            value=", ".join(current_profile.get('skills', [])),
            placeholder="Python, Java, React, Node.js, AWS, Machine Learning",
            height=100
        )
        
        st.markdown("---")
        section_heading("Target Positions")
        
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

        st.markdown("---")
        section_heading("Resume")
        st.markdown("Paste your resume text — used to generate cover letters and tailored suggestions")

        resume_text = st.text_area(
            "Resume",
            value=current_profile.get('resume', ''),
            placeholder="Paste your resume as plain text...",
            height=200,
            label_visibility="collapsed"
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
                'target_companies': [c.strip() for c in target_companies.split(',') if c.strip()],
                'resume': resume_text
            }
            
            db.save_profile(user_id, profile_data)
            st.success("Profile saved successfully")
            st.rerun()

# ===== DISCOVER JOBS PAGE =====
elif page == "Discover Jobs":
    page_header("Discover Jobs", "AI-powered job recommendations tailored to your profile")
    
    profile = db.get_profile(user_id)
    
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
        get_recs = st.button("Get AI Recommendations", key="get_recs_btn", type="primary", use_container_width=True)

    if get_recs:
        loading = show_ai_loading([
            "Analyzing your profile…",
            "Scanning open roles…",
            "Matching your skills…",
            "Ranking best fits…",
        ])
        recommendations = ai.recommend_companies(profile)
        loading.empty()
        st.session_state.recommendations = recommendations
        st.session_state.show_count = 10
    
    # Display recommendations if they exist
    if 'recommendations' in st.session_state:
        st.markdown("---")
        section_heading("Recommended Companies for You")
        
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

            ring_circumference = 150.8
            ring_offset = ring_circumference * (1 - max(0, min(score_num, 100)) / 100)
            stagger = min(idx, 8)

            # Company header card with an animated circular score ring
            st.markdown(f"""
            <div class="company-card" style="--i:{stagger};">
                <div class="score-ring">
                    <svg viewBox="0 0 56 56" width="54" height="54">
                        <circle class="ring-track" cx="28" cy="28" r="24" />
                        <circle class="ring-progress" cx="28" cy="28" r="24"
                            stroke="{tier_color}"
                            stroke-dasharray="{ring_circumference}"
                            stroke-dashoffset="{ring_offset}"
                            style="--i:{stagger};" />
                    </svg>
                    <div class="score-ring-inner" style="color:{tier_color}; --target-score:{score_num}; --i:{stagger};"></div>
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
                    db.add_application(user_id, new_app)
                    success_check(f"Added {company_info.get('name')} to your applications")
            
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
                            loading = show_ai_loading(
                                ["Reading the job description…", "Comparing against your profile…"],
                                show_skeleton=False,
                            )
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
                            loading.empty()
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
                        db.add_application(user_id, new_app)
                        success_check("Added to applications")
                
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

    apps = db.get_all_applications(user_id)
    stats = db.get_statistics(user_id)
    profile = db.get_profile(user_id)
    
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
                        loading = show_ai_loading(["Extracting keywords…"], show_skeleton=False)
                        keywords = ai.extract_keywords(job_desc)
                        loading.empty()

                    db.add_application(user_id, {
                        'company': company,
                        'position': position,
                        'job_url': job_url,
                        'job_description': job_desc,
                        'status': status,
                        'keywords': keywords
                    })
                    success_check(f"Added {company}")
                    st.rerun()
                else:
                    st.error("Fill in required fields")
    
    st.markdown("---")
    
    # Applications list
    if len(apps) == 0:
        st.info("No applications yet")
    else:
        section_heading(f"Applications ({len(apps)})")
        
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
                        db.update_application(user_id, app['id'], {'status': new_status})
                        st.success("Updated")
                        st.rerun()
                    
                    if st.button("Delete", key=f"del_{app['id']}"):
                        db.delete_application(user_id, app['id'])
                        st.success("Deleted")
                        st.rerun()

                if st.session_state.ai_available:
                    st.markdown("---")
                    st.markdown("**AI Writing Tools**")
                    col_a, col_b = st.columns(2)

                    with col_a:
                        if st.button("Generate Cover Letter", key=f"cover_{app['id']}", use_container_width=True):
                            if not (profile and profile.get('resume')):
                                st.warning("Add your resume in Profile Setup first")
                            elif not app.get('job_description'):
                                st.warning("This application has no job description saved")
                            else:
                                loading = show_ai_loading(
                                    ["Reading the job description…", "Drafting your cover letter…"],
                                    show_skeleton=False,
                                )
                                letter = ai.generate_cover_letter(
                                    app.get('company', ''),
                                    app.get('position', ''),
                                    app.get('job_description', ''),
                                    profile.get('resume', '')
                                )
                                loading.empty()
                                st.session_state[f'cover_letter_{app["id"]}'] = letter

                    with col_b:
                        if st.button("Improve My Resume", key=f"resumetips_{app['id']}", use_container_width=True):
                            if not (profile and profile.get('resume')):
                                st.warning("Add your resume in Profile Setup first")
                            elif not app.get('job_description'):
                                st.warning("This application has no job description saved")
                            else:
                                loading = show_ai_loading(
                                    ["Comparing your resume to this role…"],
                                    show_skeleton=False,
                                )
                                tips = ai.customize_resume(profile.get('resume', ''), app.get('job_description', ''))
                                loading.empty()
                                st.session_state[f'resume_tips_{app["id"]}'] = tips

                    if f'cover_letter_{app["id"]}' in st.session_state:
                        st.markdown("#### Cover Letter")
                        st.markdown(st.session_state[f'cover_letter_{app["id"]}'])

                    if f'resume_tips_{app["id"]}' in st.session_state:
                        st.markdown("#### Resume Suggestions")
                        st.markdown(st.session_state[f'resume_tips_{app["id"]}'])

# ===== PORTFOLIO PAGE =====
elif page == "Portfolio":
    page_header("Portfolio", "Turn your projects into polished, AI-written portfolio entries")

    projects = db.get_portfolio_projects(user_id)

    col1, col2, col3 = st.columns(3)
    col1.metric("Projects", len(projects))
    col2.metric("Written", len([p for p in projects if p.get('generated')]))
    col3.metric("Drafts", len([p for p in projects if not p.get('generated')]))

    st.markdown("---")

    with st.expander("Add New Project"):
        with st.form("new_project"):
            title = st.text_input("Project Title", placeholder="AI Job Search Platform")
            col1, col2 = st.columns(2)
            with col1:
                role = st.text_input("Your Role", placeholder="Full-stack developer")
            with col2:
                tech_stack = st.text_input("Tech Stack", placeholder="Python, Streamlit, Claude API, MongoDB")

            description = st.text_area(
                "What did you build and why? (raw notes are fine)",
                height=150,
                placeholder="Built a job search platform that uses Claude API to..."
            )
            outcome = st.text_area(
                "Outcome / Impact (optional)",
                height=80,
                placeholder="Deployed and used daily; improved Lighthouse accessibility score from 88 to 94"
            )

            submit_project = st.form_submit_button("Add Project", type="primary", use_container_width=True)

            if submit_project:
                if title and description:
                    db.add_portfolio_project(user_id, {
                        'title': title,
                        'role': role,
                        'tech_stack': tech_stack,
                        'description': description,
                        'outcome': outcome,
                    })
                    success_check(f"Added {title}")
                    st.rerun()
                else:
                    st.error("Title and description are required")

    st.markdown("---")

    if len(projects) == 0:
        st.info("No projects yet — add one above")
    else:
        section_heading(f"Projects ({len(projects)})")

        for project in projects:
            with st.expander(project.get('title', 'Untitled Project')):
                st.write(f"**Role:** {project.get('role') or 'N/A'}")
                st.write(f"**Tech Stack:** {project.get('tech_stack') or 'N/A'}")
                st.write(f"**Notes:** {project.get('description', 'N/A')}")
                if project.get('outcome'):
                    st.write(f"**Outcome:** {project.get('outcome')}")

                col_a, col_b = st.columns([1, 1])

                with col_a:
                    if not st.session_state.ai_available:
                        st.caption("AI features unavailable. Check API configuration.")
                    else:
                        button_label = "Regenerate" if project.get('generated') else "Generate Portfolio Entry"
                        if st.button(button_label, key=f"genport_{project['id']}", type="primary", use_container_width=True):
                            loading = show_ai_loading(["Writing your portfolio entry…"], show_skeleton=False)
                            content = ai.generate_portfolio_content(project)
                            loading.empty()
                            db.update_portfolio_project(user_id, project['id'], {'generated': content})
                            st.rerun()

                with col_b:
                    if st.button("Delete", key=f"delport_{project['id']}", use_container_width=True):
                        db.delete_portfolio_project(user_id, project['id'])
                        st.rerun()

                if project.get('generated'):
                    st.markdown("---")
                    st.markdown("#### Portfolio Entry")
                    st.markdown(project['generated'])

# ===== ANALYTICS PAGE =====
elif page == "Analytics":
    page_header("Analytics", "Job search insights")
    
    apps = db.get_all_applications(user_id)
    stats = db.get_statistics(user_id)
    
    if len(apps) == 0:
        st.info("No data yet")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            section_heading("Status Distribution")

            status_df = pd.DataFrame({
                "Status": ["Applied", "Interview", "Offer", "Rejected"],
                "Count": [stats['applied'], stats['interview'], stats['offer'], stats['rejected']],
            })
            axis = alt.Axis(
                labelColor=palette["text-muted"],
                titleColor=palette["text-muted"],
                domainColor=palette["border"],
                tickColor=palette["border"],
                gridColor=palette["border"],
            )
            chart = alt.Chart(status_df).mark_bar(color=palette["accent"], size=40).encode(
                x=alt.X("Status", sort=None, title=None, axis=axis),
                y=alt.Y("Count", title=None, axis=axis),
            ).properties(background=palette["bg"])
            st.altair_chart(chart, use_container_width=True)
        
        with col2:
            section_heading("Recent Activity")

            status_color = {
                "Applied": "var(--accent)",
                "Interview": "var(--warning)",
                "Offer": "var(--success)",
                "Rejected": "var(--danger)",
            }

            items = "".join(f"""
                <div class="timeline-item" style="--dot-color: {status_color.get(app.get('status'), 'var(--accent)')}; --i:{i};">
                    <div class="t-title">{app['company']} &mdash; {app['position']}</div>
                    <div class="t-meta">{app['status']} on {app['date_applied']}</div>
                </div>
            """ for i, app in enumerate(apps[:5]))

            st.markdown(f'<div class="timeline">{items}</div>', unsafe_allow_html=True)