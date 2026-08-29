import os
import re
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.validator import Validator as _AuthValidator
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

if "lang" not in st.session_state:
    st.session_state.lang = "ko"

# ===== Translations =====
# Only static app chrome lives here. AI-generated text (recommendations,
# cover letters, analysis) is translated separately by asking the model to
# respond in the selected language — see ai_helper.py.
T = {
    "landing_title_1": {"ko": "취업 준비,", "en": "Your job search,"},
    "landing_title_2": {"ko": "이제 한 곳에서.", "en": "finally organized."},
    "landing_lede": {"ko": "지원 현황을 한눈에 관리하고, 나에게 맞는 공고를 추천받으세요.",
                      "en": "Track every application. Get matched to roles that actually fit."},
    "landing_cta": {"ko": "시작하기", "en": "Get Started"},
    "landing_eyebrow": {"ko": "AI 커리어 플랫폼", "en": "AI Career Platform"},
    "landing_caption": {"ko": "실제 채용공고 확인 기반 매칭, 내 이력서로 작성하는 자소서.",
                         "en": "Matches checked against real postings. Cover letters written from your own resume."},

    "auth_title": {"ko": "Job Platform", "en": "Job Platform"},
    "auth_subtitle": {"ko": "로그인하고 지원 현황을 관리하고, AI 맞춤 추천과 포트폴리오까지 만들어보세요",
                       "en": "Sign in to track applications, get AI-matched recommendations, and build your portfolio"},
    "auth_error": {"ko": "아이디 또는 비밀번호가 올바르지 않습니다", "en": "Username or password is incorrect"},
    "auth_register_expander": {"ko": "처음이신가요? 계정 만들기", "en": "New here? Create an account"},
    "auth_register_success": {"ko": "{name}님 계정이 생성되었습니다 — 위에서 로그인해주세요",
                               "en": "Account created for {name} — log in above"},

    "sidebar_brand_name": {"ko": "Job Platform", "en": "Job Platform"},
    "sidebar_brand_sub": {"ko": "커리어 인텔리전스", "en": "CAREER INTELLIGENCE"},
    "sidebar_signed_in": {"ko": "로그인 계정", "en": "Signed in as"},
    "sidebar_setup_required": {"ko": "설정 필요", "en": "Setup required"},
    "sidebar_setup_desc": {"ko": "프로필을 완성해주세요", "en": "Complete your profile"},
    "nav_profile": {"ko": "프로필 설정", "en": "Profile Setup"},
    "nav_discover": {"ko": "채용 탐색", "en": "Discover Jobs"},
    "nav_applications": {"ko": "내 지원 현황", "en": "My Applications"},
    "nav_portfolio": {"ko": "포트폴리오", "en": "Portfolio"},
    "nav_analytics": {"ko": "분석", "en": "Analytics"},
    "sidebar_stat_applications": {"ko": "지원 건수", "en": "Applications"},
    "sidebar_stat_interviews": {"ko": "면접", "en": "Interviews"},
    "dark_mode": {"ko": "다크 모드", "en": "Dark Mode"},
    "log_out": {"ko": "로그아웃", "en": "Log Out"},

    "profile_page_title": {"ko": "프로필 설정", "en": "Profile Setup"},
    "profile_page_sub": {"ko": "맞춤 추천을 받으려면 프로필을 설정하세요",
                          "en": "Set up your profile to get personalized job recommendations"},
    "profile_section_basic": {"ko": "기본 정보", "en": "Basic Information"},
    "profile_section_skills": {"ko": "기술 스택", "en": "Technical Skills"},
    "profile_section_targets": {"ko": "희망 직무", "en": "Target Positions"},
    "profile_section_resume": {"ko": "이력서", "en": "Resume"},
    "profile_full_name": {"ko": "이름", "en": "Full Name"},
    "profile_name_placeholder": {"ko": "예: 홍길동", "en": "e.g. Jane Doe"},
    "profile_education": {"ko": "학력", "en": "Education"},
    "profile_education_placeholder": {"ko": "예: OO대학교 컴퓨터공학과 학사, 2024",
                                       "en": "e.g. B.S. Computer Science, State University, 2024"},
    "profile_experience": {"ko": "경력", "en": "Experience Level"},
    "profile_location": {"ko": "희망 지역", "en": "Target Location"},
    "profile_location_placeholder": {"ko": "예: 서울, 대한민국 / 베이 에어리어, 미국",
                                      "en": "e.g. Seoul, Korea / Bay Area, USA"},
    "profile_skills_hint": {"ko": "보유 기술을 쉼표로 구분해서 입력하세요", "en": "Enter your skills (comma-separated)"},
    "profile_skills": {"ko": "기술 스택", "en": "Skills"},
    "profile_roles": {"ko": "희망 직무", "en": "Roles of Interest"},
    "profile_companies": {"ko": "관심 기업 (선택)", "en": "Companies of Interest (Optional)"},
    "profile_resume_hint": {"ko": "이력서 원문을 붙여넣으세요 — 자소서와 맞춤 제안 생성에 사용됩니다",
                             "en": "Paste your resume text — used to generate cover letters and tailored suggestions"},
    "profile_resume_placeholder": {"ko": "이력서를 텍스트로 붙여넣으세요...", "en": "Paste your resume as plain text..."},
    "profile_save": {"ko": "프로필 저장", "en": "Save Profile"},
    "profile_saved": {"ko": "프로필이 저장되었습니다", "en": "Profile saved successfully"},

    "discover_page_title": {"ko": "채용 탐색", "en": "Discover Jobs"},
    "discover_page_sub": {"ko": "내 프로필에 맞춘 AI 채용 추천", "en": "AI-powered job recommendations tailored to your profile"},
    "discover_need_profile": {"ko": "맞춤 추천을 받으려면 먼저 프로필을 완성해주세요",
                               "en": "Complete your profile first to get personalized recommendations"},
    "discover_need_profile_hint": {"ko": "사이드바에서 '프로필 설정'으로 이동하세요",
                                    "en": "Use the sidebar to navigate to 'Profile Setup'"},
    "ai_unavailable": {"ko": "AI 기능을 사용할 수 없습니다. API 설정을 확인하세요.",
                        "en": "AI features unavailable. Check API configuration."},
    "discover_profile_summary": {"ko": "내 프로필 요약", "en": "Your Profile Summary"},
    "discover_get_recs": {"ko": "AI 추천 받기", "en": "Get AI Recommendations"},
    "loading_analyzing_profile": {"ko": "프로필을 분석하고 있습니다…", "en": "Analyzing your profile…"},
    "loading_scanning_roles": {"ko": "공고를 검색하고 있습니다…", "en": "Scanning open roles…"},
    "loading_matching_skills": {"ko": "기술 스택을 매칭하고 있습니다…", "en": "Matching your skills…"},
    "loading_ranking_fits": {"ko": "최적의 매칭을 정리하고 있습니다…", "en": "Ranking best fits…"},
    "loading_reading_jd": {"ko": "채용공고를 읽고 있습니다…", "en": "Reading the job description…"},
    "loading_comparing_profile": {"ko": "프로필과 비교하고 있습니다…", "en": "Comparing against your profile…"},
    "loading_looking_up_culture": {"ko": "기업 문화를 검색하고 있습니다…", "en": "Looking up company values…"},
    "loading_aligning_resume": {"ko": "이력서를 정리하고 있습니다…", "en": "Aligning your resume…"},
    "loading_drafting_letter": {"ko": "자소서를 작성하고 있습니다…", "en": "Drafting your cover letter…"},
    "loading_comparing_role": {"ko": "이력서를 채용공고와 비교하고 있습니다…", "en": "Comparing your resume to this role…"},
    "loading_scoring_resume": {"ko": "채용공고 대비 이력서 점수를 매기고 있습니다…", "en": "Scoring your resume against this posting…"},
    "loading_extracting_keywords": {"ko": "핵심 키워드를 추출하고 있습니다…", "en": "Extracting keywords…"},
    "loading_writing_portfolio": {"ko": "포트폴리오 항목을 작성하고 있습니다…", "en": "Writing your portfolio entry…"},
    "profile_summary_name": {"ko": "이름", "en": "Name"},
    "profile_summary_education": {"ko": "학력", "en": "Education"},
    "profile_summary_experience": {"ko": "경력", "en": "Experience"},
    "profile_summary_location": {"ko": "희망 지역", "en": "Location"},
    "profile_summary_skills": {"ko": "기술", "en": "Skills"},
    "profile_summary_more": {"ko": "... 외 {count}개", "en": "... and {count} more"},
    "discover_recommended": {"ko": "추천 기업", "en": "Recommended Companies for You"},
    "tier_strong": {"ko": "매우 적합", "en": "Strong fit"},
    "tier_good": {"ko": "적합", "en": "Good fit"},
    "tier_possible": {"ko": "다소 적합", "en": "Possible fit"},
    "tier_na": {"ko": "점수 확인 불가", "en": "Score unavailable"},
    "posting_found": {"ko": "🔗 공고 확인됨", "en": "🔗 Posting found"},
    "posting_unconfirmed": {"ko": "공고 미확인", "en": "Posting not confirmed"},
    "why_good_match": {"ko": "매칭 이유", "en": "Why Good Match"},
    "view_details": {"ko": "상세 보기", "en": "View Details"},
    "requirements": {"ko": "자격 요건", "en": "Requirements"},
    "culture_notes": {"ko": "기업 문화", "en": "Culture Notes"},
    "gaps": {"ko": "부족한 점", "en": "Gaps"},
    "add_to_applications": {"ko": "지원 목록에 추가", "en": "Add to Applications"},
    "added_to_applications": {"ko": "{name}을(를) 지원 목록에 추가했습니다", "en": "Added {name} to your applications"},
    "view_detailed_analysis": {"ko": "상세 분석 보기", "en": "View Detailed Analysis"},
    "paste_jd_for_analysis": {"ko": "상세 분석을 위해 채용공고를 붙여넣으세요", "en": "Paste Job Description for detailed analysis"},
    "paste_jd_placeholder": {"ko": "실제 채용공고를 붙여넣으세요...", "en": "Paste the actual job description here..."},
    "generate_analysis": {"ko": "분석 생성", "en": "Generate Analysis"},
    "please_paste_jd": {"ko": "채용공고를 붙여넣어주세요", "en": "Please paste a job description"},
    "added_to_applications_simple": {"ko": "지원 목록에 추가했습니다", "en": "Added to applications"},
    "analysis_results": {"ko": "분석 결과", "en": "Analysis Results"},
    "learning_roadmap": {"ko": "학습 로드맵", "en": "Learning Roadmap"},
    "strengthen_resume_btn": {"ko": "이 기업 문화에 맞춰 이력서 보강하기", "en": "Strengthen Resume for This Company's Culture"},
    "add_resume_first": {"ko": "프로필 설정에서 먼저 이력서를 추가해주세요", "en": "Add a resume in Profile Setup first"},
    "resume_alignment_suggestions": {"ko": "이력서 보강 제안", "en": "Resume Alignment Suggestions"},
    "load_more": {"ko": "5개 더 보기", "en": "Load More (5 more)"},
    "showing_of_companies": {"ko": "{shown}개 / 총 {total}개 기업", "en": "Showing {shown} of {total} companies"},

    "apps_page_title": {"ko": "내 지원 현황", "en": "My Applications"},
    "apps_page_sub": {"ko": "지원 현황을 추적하고 관리하세요", "en": "Track and manage your job applications"},
    "stat_total": {"ko": "전체", "en": "Total"},
    "stat_applied": {"ko": "지원함", "en": "Applied"},
    "stat_interviews": {"ko": "면접", "en": "Interviews"},
    "stat_offers": {"ko": "합격", "en": "Offers"},
    "add_new_application": {"ko": "새 지원 추가", "en": "Add New Application"},
    "added_company": {"ko": "{name} 추가되었습니다", "en": "Added {name}"},
    "company_name": {"ko": "회사명", "en": "Company Name"},
    "position": {"ko": "직무", "en": "Position"},
    "job_url": {"ko": "채용공고 링크", "en": "Job URL"},
    "status": {"ko": "상태", "en": "Status"},
    "job_description": {"ko": "채용공고 내용", "en": "Job Description"},
    "paste_jd_short": {"ko": "채용공고를 붙여넣으세요", "en": "Paste job description"},
    "save": {"ko": "저장", "en": "Save"},
    "fill_required_fields": {"ko": "필수 항목을 입력해주세요", "en": "Fill in required fields"},
    "no_applications_yet": {"ko": "아직 지원한 곳이 없습니다", "en": "No applications yet"},
    "applications_count": {"ko": "지원 현황 ({count}건)", "en": "Applications ({count})"},
    "search": {"ko": "검색", "en": "Search"},
    "filter": {"ko": "필터", "en": "Filter"},
    "filter_all": {"ko": "전체", "en": "All"},
    "applied_on": {"ko": "지원일", "en": "Applied"},
    "job_posting_link": {"ko": "채용공고 보기", "en": "Job Posting"},
    "ai_analysis": {"ko": "AI 분석", "en": "AI Analysis"},
    "update": {"ko": "상태 변경", "en": "Update"},
    "delete": {"ko": "삭제", "en": "Delete"},
    "updated": {"ko": "변경되었습니다", "en": "Updated"},
    "deleted": {"ko": "삭제되었습니다", "en": "Deleted"},
    "ai_writing_tools": {"ko": "AI 작성 도구", "en": "AI Writing Tools"},
    "generate_cover_letter": {"ko": "자소서 생성", "en": "Generate Cover Letter"},
    "improve_resume": {"ko": "이력서 개선 제안", "en": "Improve My Resume"},
    "check_match_score": {"ko": "매칭 점수 확인", "en": "Check Match Score"},
    "add_resume_warning": {"ko": "프로필 설정에서 이력서를 먼저 추가해주세요", "en": "Add your resume in Profile Setup first"},
    "no_jd_warning": {"ko": "이 지원 건에는 저장된 채용공고가 없습니다", "en": "This application has no job description saved"},
    "cover_letter_heading": {"ko": "자기소개서", "en": "Cover Letter"},
    "resume_suggestions_heading": {"ko": "이력서 개선 제안", "en": "Resume Suggestions"},
    "match_score_heading": {"ko": "매칭 점수", "en": "Match Score"},

    "portfolio_page_title": {"ko": "포트폴리오", "en": "Portfolio"},
    "portfolio_page_sub": {"ko": "프로젝트를 AI가 다듬은 포트폴리오 항목으로 만들어보세요",
                            "en": "Turn your projects into polished, AI-written portfolio entries"},
    "portfolio_stat_projects": {"ko": "프로젝트", "en": "Projects"},
    "portfolio_stat_written": {"ko": "작성 완료", "en": "Written"},
    "portfolio_stat_drafts": {"ko": "초안", "en": "Drafts"},
    "add_new_project": {"ko": "새 프로젝트 추가", "en": "Add New Project"},
    "project_title": {"ko": "프로젝트 제목", "en": "Project Title"},
    "your_role": {"ko": "맡은 역할", "en": "Your Role"},
    "tech_stack": {"ko": "기술 스택", "en": "Tech Stack"},
    "project_desc_label": {"ko": "무엇을 만들었고 왜 만들었나요? (초안 메모여도 괜찮습니다)",
                            "en": "What did you build and why? (raw notes are fine)"},
    "project_outcome_label": {"ko": "성과 / 임팩트 (선택)", "en": "Outcome / Impact (optional)"},
    "add_project": {"ko": "프로젝트 추가", "en": "Add Project"},
    "title_desc_required": {"ko": "제목과 설명은 필수입니다", "en": "Title and description are required"},
    "no_projects_yet": {"ko": "아직 프로젝트가 없습니다 — 위에서 추가해보세요", "en": "No projects yet — add one above"},
    "projects_count": {"ko": "프로젝트 ({count}건)", "en": "Projects ({count})"},
    "role_label": {"ko": "역할", "en": "Role"},
    "notes_label": {"ko": "메모", "en": "Notes"},
    "outcome_label": {"ko": "성과", "en": "Outcome"},
    "regenerate": {"ko": "다시 생성", "en": "Regenerate"},
    "generate_portfolio_entry": {"ko": "포트폴리오 항목 생성", "en": "Generate Portfolio Entry"},
    "portfolio_entry_heading": {"ko": "포트폴리오 항목", "en": "Portfolio Entry"},

    "analytics_page_title": {"ko": "분석", "en": "Analytics"},
    "analytics_page_sub": {"ko": "지원 현황 인사이트", "en": "Job search insights"},
    "no_data_yet": {"ko": "아직 데이터가 없습니다", "en": "No data yet"},
    "status_distribution": {"ko": "상태별 분포", "en": "Status Distribution"},
    "recent_activity": {"ko": "최근 활동", "en": "Recent Activity"},
    "timeline_meta": {"ko": "{status} · {date}", "en": "{status} on {date}"},
}


def t(key):
    return T[key][st.session_state.lang]


STATUS_VALUES = ["Applied", "Interview", "Offer", "Rejected"]
STATUS_LABELS = {
    "ko": {"Applied": "지원함", "Interview": "면접", "Offer": "합격", "Rejected": "불합격"},
    "en": {"Applied": "Applied", "Interview": "Interview", "Offer": "Offer", "Rejected": "Rejected"},
}


def status_label(value):
    return STATUS_LABELS[st.session_state.lang].get(value, value)


EXPERIENCE_VALUES = ["New Graduate", "0-1 years", "1-3 years", "3-5 years", "5+ years"]
EXPERIENCE_LABELS = {
    "ko": {"New Graduate": "신입", "0-1 years": "0-1년", "1-3 years": "1-3년",
           "3-5 years": "3-5년", "5+ years": "5년 이상"},
    "en": {v: v for v in EXPERIENCE_VALUES},
}


def experience_label(value):
    return EXPERIENCE_LABELS[st.session_state.lang].get(value, value)


def render_lang_toggle(key):
    current = st.session_state.lang
    choice = st.radio(
        "Language", ["한국어", "English"],
        index=0 if current == "ko" else 1,
        horizontal=True, label_visibility="collapsed", key=key,
    )
    st.session_state.lang = "ko" if choice == "한국어" else "en"


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

    /* Widget labels (text_input/text_area/selectbox captions) default to a
       fixed color that isn't aware of the dark-mode palette, making them
       nearly invisible on a black background. */
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label {
        color: var(--text-muted) !important;
    }

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
    .posting-badge {
        display: inline-block;
        margin-left: 0.5rem;
        padding: 0.1rem 0.55rem;
        border-radius: 980px;
        font-size: 0.72rem;
        font-weight: 500;
        vertical-align: middle;
    }
    .posting-badge.found { background: var(--accent-tint); color: var(--accent-text); }
    .posting-badge.unconfirmed { background: var(--hover-tint); color: var(--text-muted); }
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
    .score-ring-inner.na { animation: none; }
    .score-ring-inner.na::after { content: '—'; }
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


def render_landing_page():
    """Landing splash shown once before the login screen.

    A headline, one line of copy, one action — nothing else."""
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] [data-testid="stMain"] .block-container {
            padding-top: 6.5rem;
            max-width: 820px;
        }
        /* Streamlit appends an anchor-link icon to headings; it reads as a
           stray glyph next to the headline here. */
        .landing h1 a, .landing h1 svg { display: none !important; }
        .landing { text-align: center; padding: 2rem 1rem 0; }
        .landing-eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin: 0 0 1.6rem;
            opacity: 0;
            animation: fadeInUp 0.6s ease-out forwards;
        }
        .landing-eyebrow::before {
            content: "";
            display: inline-block;
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--accent);
        }
        .landing h1 {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display",
                "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
            font-size: clamp(2.6rem, 6vw, 4rem) !important;
            font-weight: 600 !important;
            letter-spacing: -0.035em;
            line-height: 1.06;
            color: var(--text) !important;
            margin: 0 0 1.3rem;
            opacity: 0;
            animation: fadeInUp 0.65s ease-out 0.08s forwards;
        }
        .landing-rule {
            width: 44px;
            height: 3px;
            background: var(--text);
            margin: 0 auto 1.6rem;
            opacity: 0;
            animation: fadeInUp 0.6s ease-out 0.18s forwards;
        }
        .landing .lede {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text",
                "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: clamp(1.1rem, 2vw, 1.35rem);
            font-weight: 400;
            line-height: 1.45;
            color: var(--text-muted);
            max-width: 36ch;
            margin: 0 auto;
            opacity: 0;
            animation: fadeInUp 0.6s ease-out 0.26s forwards;
        }
        .landing-caption {
            text-align: center;
            font-size: 0.9rem;
            color: var(--text-muted);
            margin: 2.2rem 0 4.5rem;
            opacity: 0;
            animation: fadeInUp 0.6s ease-out 0.42s forwards;
        }
        /* Monochrome pill CTA — the blue default read as generic. */
        .st-key-landing_cta {
            max-width: 210px;
            margin: 2.6rem auto 0;
            opacity: 0;
            animation: fadeInUp 0.6s ease-out 0.34s forwards;
        }
        .st-key-landing_cta .stButton>button[kind="primary"] {
            background: var(--text);
            border: 1px solid var(--text);
            color: var(--bg);
            font-weight: 600;
            letter-spacing: -0.01em;
            height: 3.2em;
            transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
        }
        .st-key-landing_cta .stButton>button[kind="primary"]:hover {
            background: var(--text-muted);
            border-color: var(--text-muted);
            color: var(--bg);
            transform: translateY(-1px);
        }
        .st-key-landing_lang { max-width: 200px; margin: 0 auto; }
        </style>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        render_lang_toggle("landing_lang")

    st.markdown(f"""
        <div class="landing">
            <div class="landing-eyebrow">{t('landing_eyebrow')}</div>
            <h1>{t('landing_title_1')}<br/>{t('landing_title_2')}</h1>
            <div class="landing-rule"></div>
            <p class="lede">{t('landing_lede')}</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button(t('landing_cta'), key="landing_cta", type="primary", use_container_width=True):
            st.session_state.show_landing = False
            st.rerun()

    st.markdown(
        f'<p class="landing-caption">{t("landing_caption")}</p>',
        unsafe_allow_html=True,
    )


# ===== AUTH GATE =====
LOGIN_FIELDS = {
    "ko": {"Form name": "로그인", "Username": "아이디", "Password": "비밀번호", "Login": "로그인"},
    "en": {"Form name": "Login", "Username": "Username", "Password": "Password", "Login": "Login"},
}
REGISTER_FIELDS = {
    "ko": {"Form name": "계정 만들기", "First name": "이름", "Last name": "성",
           "Email": "이메일", "Username": "아이디", "Password": "비밀번호",
           "Repeat password": "비밀번호 확인", "Password hint": "비밀번호 힌트", "Register": "가입하기"},
    "en": {"Form name": "Register user", "First name": "First name", "Last name": "Last name",
           "Email": "Email", "Username": "Username", "Password": "Password",
           "Repeat password": "Repeat password", "Password hint": "Password hint", "Register": "Register"},
}

class _KoreanNameValidator(_AuthValidator):
    """The library's default name pattern requires 2+ characters, which
    rejects one-syllable Korean surnames (김, 이, 박, ...). Same character
    set, minimum length of 1 instead."""
    def validate_name(self, name):
        pattern = r"^[A-Za-zÀ-ɏͰ-῿Ⰰ-퟿一-鿿' .-]{1,100}$"
        return bool(re.match(pattern, name, re.UNICODE))


credentials = {'usernames': db.get_all_users()}
cookie_key = os.getenv("AUTH_COOKIE_KEY", "dev-only-insecure-key-set-AUTH_COOKIE_KEY-in-production")
authenticator = stauth.Authenticate(
    credentials, "job_platform_auth", cookie_key, 30, validator=_KoreanNameValidator()
)

authenticator.login(location='unrendered')
auth_status = st.session_state.get("authentication_status")

if not auth_status:
    st.session_state.setdefault('show_landing', True)
    if st.session_state.show_landing:
        render_landing_page()
        st.stop()

    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_b:
        render_lang_toggle("auth_lang")

    page_header(t('auth_title'), t('auth_subtitle'))

    authenticator.login(clear_on_submit=True, fields=LOGIN_FIELDS[st.session_state.lang])
    auth_status = st.session_state.get("authentication_status")
    if auth_status is False:
        st.error(t('auth_error'))

    with st.expander(t('auth_register_expander')):
        try:
            email, new_username, name = authenticator.register_user(
                captcha=False, fields=REGISTER_FIELDS[st.session_state.lang]
            )
            if email:
                db.create_user(new_username, credentials['usernames'][new_username])
                success_check(t('auth_register_success').format(name=name))
        except Exception as e:
            st.error(str(e))

    st.stop()

user_id = st.session_state["username"]

# Sidebar
NAV_PAGES = ["Profile Setup", "Discover Jobs", "My Applications", "Portfolio", "Analytics"]
NAV_KEYS = {
    "Profile Setup": "nav_profile", "Discover Jobs": "nav_discover",
    "My Applications": "nav_applications", "Portfolio": "nav_portfolio", "Analytics": "nav_analytics",
}

with st.sidebar:
    render_lang_toggle("sidebar_lang")

    st.markdown(f"""
        <div class="brand">
            <span class="brand-mark"></span>
            <div>
                <div class="brand-name">{t('sidebar_brand_name')}</div>
                <div class="brand-sub">{t('sidebar_brand_sub')}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    profile = db.get_profile(user_id)
    if profile:
        st.markdown(f"""
            <div class="profile-chip">
                <div class="label">{t('sidebar_signed_in')}</div>
                <div class="value">{profile.get('name', 'User')}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="profile-chip">
                <div class="label">{t('sidebar_setup_required')}</div>
                <div class="value">{t('sidebar_setup_desc')}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "Navigation",
        NAV_PAGES,
        format_func=lambda p: t(NAV_KEYS[p]),
        label_visibility="collapsed"
    )

    st.markdown("---")
    stats = db.get_statistics(user_id)
    col1, col2 = st.columns(2)
    col1.metric(t('sidebar_stat_applications'), stats['total'])
    col2.metric(t('sidebar_stat_interviews'), stats['interview'])

    st.markdown("---")
    st.toggle(t('dark_mode'), key="dark_mode")
    authenticator.logout(t('log_out'), "sidebar", use_container_width=True)

    st.markdown('<div class="sidebar-footer">Built by Sunghoon Lee</div>', unsafe_allow_html=True)

# ===== PROFILE SETUP PAGE =====
if page == "Profile Setup":
    page_header(t('profile_page_title'), t('profile_page_sub'))

    current_profile = db.get_profile(user_id) or {}

    with st.form("profile_form"):
        section_heading(t('profile_section_basic'))

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(
                t('profile_full_name'),
                value=current_profile.get('name', ''),
                placeholder=t('profile_name_placeholder')
            )
            education = st.text_input(
                t('profile_education'),
                value=current_profile.get('education', ''),
                placeholder=t('profile_education_placeholder')
            )

        with col2:
            experience = st.selectbox(
                t('profile_experience'),
                EXPERIENCE_VALUES,
                index=EXPERIENCE_VALUES.index(current_profile.get('experience', 'New Graduate')),
                format_func=experience_label,
            )
            target_location = st.text_input(
                t('profile_location'),
                value=current_profile.get('target_location', ''),
                placeholder=t('profile_location_placeholder')
            )

        st.markdown("---")
        section_heading(t('profile_section_skills'))
        st.markdown(t('profile_skills_hint'))

        skills_input = st.text_area(
            t('profile_skills'),
            value=", ".join(current_profile.get('skills', [])),
            placeholder="Python, Java, React, Node.js, AWS, Machine Learning",
            height=100
        )

        st.markdown("---")
        section_heading(t('profile_section_targets'))

        col1, col2 = st.columns(2)
        with col1:
            target_roles = st.text_area(
                t('profile_roles'),
                value=", ".join(current_profile.get('target_roles', [])),
                placeholder="Software Engineer, Data Scientist, Backend Developer",
                height=100
            )

        with col2:
            target_companies = st.text_area(
                t('profile_companies'),
                value=", ".join(current_profile.get('target_companies', [])),
                placeholder="Samsung, SK Hynix, Google, Naver",
                height=100
            )

        st.markdown("---")
        section_heading(t('profile_section_resume'))
        st.markdown(t('profile_resume_hint'))

        resume_text = st.text_area(
            "Resume",
            value=current_profile.get('resume', ''),
            placeholder=t('profile_resume_placeholder'),
            height=200,
            label_visibility="collapsed"
        )

        submitted = st.form_submit_button(t('profile_save'), type="primary")

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
            st.success(t('profile_saved'))
            st.rerun()

# ===== DISCOVER JOBS PAGE =====
elif page == "Discover Jobs":
    page_header(t('discover_page_title'), t('discover_page_sub'))

    profile = db.get_profile(user_id)

    if not profile:
        st.warning(t('discover_need_profile'))
        st.info(t('discover_need_profile_hint'))
        st.stop()

    if not st.session_state.ai_available:
        st.error(t('ai_unavailable'))
        st.stop()

    # Profile summary
    with st.expander(t('discover_profile_summary'), expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**{t('profile_summary_name')}:** {profile.get('name', 'N/A')}")
            st.write(f"**{t('profile_summary_education')}:** {profile.get('education', 'N/A')}")
            st.write(f"**{t('profile_summary_experience')}:** {experience_label(profile.get('experience', 'N/A'))}")
        with col2:
            st.write(f"**{t('profile_summary_location')}:** {profile.get('target_location', 'N/A')}")
            st.write(f"**{t('profile_summary_skills')}:** {', '.join(profile.get('skills', [])[:5])}")
            if len(profile.get('skills', [])) > 5:
                st.write(t('profile_summary_more').format(count=len(profile.get('skills', [])) - 5))

    st.markdown("---")

    # Get recommendations button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        get_recs = st.button(t('discover_get_recs'), key="get_recs_btn", type="primary", use_container_width=True)

    if get_recs:
        loading = show_ai_loading([
            t('loading_analyzing_profile'),
            t('loading_scanning_roles'),
            t('loading_matching_skills'),
            t('loading_ranking_fits'),
        ])
        recommendations = ai.recommend_companies(profile, lang=st.session_state.lang)
        loading.empty()
        st.session_state.recommendations = recommendations
        st.session_state.show_count = 10

    # Display recommendations if they exist
    if 'recommendations' in st.session_state:
        st.markdown("---")
        section_heading(t('discover_recommended'))
        
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
                elif line.startswith('**Posting Status:**'):
                    company_info['posting_status'] = line.replace('**Posting Status:**', '').strip()
                elif line.startswith('**Culture Notes:**'):
                    company_info['culture_notes'] = line.replace('**Culture Notes:**', '').strip()

            if company_info.get('name'):
                all_companies.append(company_info)
        
        # Initialize show_count if not exists
        if 'show_count' not in st.session_state:
            st.session_state.show_count = 10
        
        # Display companies up to show_count
        displayed_count = min(st.session_state.show_count, len(all_companies))
        
        for idx, company_info in enumerate(all_companies[:displayed_count]):
            
            # Pull the first number out of whatever the model wrote (it doesn't
            # always stick to a bare "NN%" — "~65%", "N/A", "60-70%" all show up).
            # Defaulting a parse failure to 0% would silently show "Possible fit"
            # in red for a company we simply couldn't read a score for, which
            # misrepresents it as a bad match rather than an unscored one.
            score_digits = re.search(r'\d+', company_info.get('score', ''))
            score_num = int(score_digits.group()) if score_digits else None

            if score_num is None:
                tier_color, tier_label = "var(--text-muted)", t('tier_na')
            elif score_num >= 80:
                tier_color, tier_label = "var(--success)", t('tier_strong')
            elif score_num >= 60:
                tier_color, tier_label = "var(--warning)", t('tier_good')
            else:
                tier_color, tier_label = "var(--danger)", t('tier_possible')

            ring_circumference = 150.8
            ring_offset = ring_circumference * (1 - max(0, min(score_num or 0, 100)) / 100)
            ring_inner_class = "score-ring-inner na" if score_num is None else "score-ring-inner"
            stagger = min(idx, 8)

            posting_status = company_info.get('posting_status', '')
            posting_match = re.match(r'Found:\s*(\S+)', posting_status)
            if posting_match:
                posting_badge = f'<a href="{posting_match.group(1)}" target="_blank" class="posting-badge found">{t("posting_found")}</a>'
            else:
                posting_badge = f'<span class="posting-badge unconfirmed">{t("posting_unconfirmed")}</span>'

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
                    <div class="{ring_inner_class}" style="color:{tier_color}; --target-score:{score_num or 0}; --i:{stagger};"></div>
                </div>
                <div class="company-card-info">
                    <h3>{company_info.get('name', 'Unknown')} &mdash; {company_info.get('position', 'N/A')}</h3>
                    <span class="tier-label" style="color:{tier_color};">{tier_label}</span>{posting_badge}
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**{t('why_good_match')}:** {company_info.get('match', 'N/A')}")

                with st.expander(t('view_details')):
                    st.write(f"**{t('requirements')}:** {company_info.get('requirements', 'N/A')}")
                    st.write(f"**{t('culture_notes')}:** {company_info.get('culture_notes', 'Not confirmed via search')}")
                    st.write(f"**{t('gaps')}:** {company_info.get('gaps', 'N/A')}")

            with col2:
                st.markdown("<br>", unsafe_allow_html=True)

                if st.button(t('add_to_applications'), key=f"add_{idx}", type="primary", use_container_width=True):
                    new_app = {
                        'company': company_info.get('name', 'Unknown'),
                        'position': company_info.get('position', 'N/A'),
                        'job_url': '',
                        'job_description': f"Match Score: {company_info.get('score')}\n\nRequirements: {company_info.get('requirements')}\n\nGaps: {company_info.get('gaps')}",
                        'status': 'Applied',
                        'keywords': f"Match: {company_info.get('match')}"
                    }
                    db.add_application(user_id, new_app)
                    success_check(t('added_to_applications').format(name=company_info.get('name')))

            # Detailed Analysis Section
            with st.expander(t('view_detailed_analysis')):
                job_desc = st.text_area(
                    t('paste_jd_for_analysis'),
                    height=200,
                    placeholder=t('paste_jd_placeholder'),
                    key=f"job_desc_{idx}"
                )

                col_a, col_b = st.columns([1, 1])

                with col_a:
                    if st.button(t('generate_analysis'), type="primary", key=f"gen_{idx}", use_container_width=True):
                        if job_desc:
                            loading = show_ai_loading(
                                [t('loading_reading_jd'), t('loading_comparing_profile')],
                                show_skeleton=False,
                            )
                            detailed_analysis = ai.analyze_company_fit(
                                profile,
                                company_info.get('name'),
                                job_desc,
                                lang=st.session_state.lang,
                            )
                            st.session_state[f'analysis_{idx}'] = detailed_analysis

                            gaps_text = company_info.get('gaps', '')
                            if gaps_text and gaps_text != 'N/A':
                                target_skills = [s.strip() for s in gaps_text.split(',')]
                                roadmap = ai.generate_learning_roadmap(
                                    profile.get('skills', []),
                                    target_skills,
                                    lang=st.session_state.lang,
                                )
                                st.session_state[f'roadmap_{idx}'] = roadmap
                            loading.empty()
                            st.rerun()
                        else:
                            st.warning(t('please_paste_jd'))

                with col_b:
                    if st.button(t('add_to_applications'), key=f"add_detail_{idx}", use_container_width=True):
                        new_app = {
                            'company': company_info.get('name', 'Unknown'),
                            'position': company_info.get('position', 'N/A'),
                            'job_url': '',
                            'job_description': job_desc if job_desc else f"Match Score: {company_info.get('score')}\n\nRequirements: {company_info.get('requirements')}\n\nGaps: {company_info.get('gaps')}",
                            'status': 'Applied',
                            'keywords': f"Match: {company_info.get('match')}"
                        }
                        db.add_application(user_id, new_app)
                        success_check(t('added_to_applications_simple'))

                if f'analysis_{idx}' in st.session_state:
                    st.markdown("---")
                    st.markdown(f"#### {t('analysis_results')}")
                    st.markdown(st.session_state[f'analysis_{idx}'])

                if f'roadmap_{idx}' in st.session_state:
                    st.markdown("---")
                    st.markdown(f"#### {t('learning_roadmap')}")
                    st.markdown(st.session_state[f'roadmap_{idx}'])

                if st.session_state.ai_available:
                    st.markdown("---")
                    if st.button(t('strengthen_resume_btn'), key=f"strengthen_{idx}", use_container_width=True):
                        if profile.get('resume'):
                            loading = show_ai_loading(
                                [t('loading_looking_up_culture'), t('loading_aligning_resume')],
                                show_skeleton=False,
                            )
                            alignment = ai.strengthen_resume_for_company(
                                profile.get('resume', ''),
                                company_info.get('name', ''),
                                company_info.get('culture_notes', ''),
                                lang=st.session_state.lang,
                            )
                            st.session_state[f'resume_align_{idx}'] = alignment
                            loading.empty()
                            st.rerun()
                        else:
                            st.warning(t('add_resume_first'))

                if f'resume_align_{idx}' in st.session_state:
                    st.markdown("---")
                    st.markdown(f"#### {t('resume_alignment_suggestions')}")
                    st.markdown(st.session_state[f'resume_align_{idx}'])

            st.markdown("---")

        # Load More button
        if displayed_count < len(all_companies) and displayed_count < 30:
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button(t('load_more'), use_container_width=True):
                    st.session_state.show_count = min(st.session_state.show_count + 5, 30)
                    st.rerun()

        # Show count info
        st.caption(t('showing_of_companies').format(shown=displayed_count, total=min(len(all_companies), 30)))

# ===== MY APPLICATIONS PAGE =====
elif page == "My Applications":
    page_header(t('apps_page_title'), t('apps_page_sub'))

    apps = db.get_all_applications(user_id)
    stats = db.get_statistics(user_id)
    profile = db.get_profile(user_id)

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t('stat_total'), stats['total'])
    col2.metric(t('stat_applied'), stats['applied'])
    col3.metric(t('stat_interviews'), stats['interview'])
    col4.metric(t('stat_offers'), stats['offer'])

    st.markdown("---")

    # Add new application
    with st.expander(t('add_new_application')):
        with st.form("new_app"):
            col1, col2 = st.columns(2)

            with col1:
                company = st.text_input(t('company_name'), placeholder="Samsung Electronics")
                position = st.text_input(t('position'), placeholder="Software Engineer")

            with col2:
                job_url = st.text_input(t('job_url'), placeholder="https://...")
                status = st.selectbox(t('status'), STATUS_VALUES, format_func=status_label)

            job_desc = st.text_area(
                t('job_description'),
                height=200,
                placeholder=t('paste_jd_short')
            )

            col1, col2 = st.columns([3, 1])
            with col2:
                submit = st.form_submit_button(t('save'), type="primary", use_container_width=True)

            if submit:
                if company and position and job_desc:
                    keywords = None
                    if st.session_state.ai_available:
                        loading = show_ai_loading([t('loading_extracting_keywords')], show_skeleton=False)
                        keywords = ai.extract_keywords(job_desc, lang=st.session_state.lang)
                        loading.empty()

                    db.add_application(user_id, {
                        'company': company,
                        'position': position,
                        'job_url': job_url,
                        'job_description': job_desc,
                        'status': status,
                        'keywords': keywords
                    })
                    success_check(t('added_company').format(name=company))
                    st.rerun()
                else:
                    st.error(t('fill_required_fields'))

    st.markdown("---")

    # Applications list
    if len(apps) == 0:
        st.info(t('no_applications_yet'))
    else:
        section_heading(t('applications_count').format(count=len(apps)))

        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input(t('search'), "")
        with col2:
            filter_status = st.selectbox(
                t('filter'), ["All"] + STATUS_VALUES,
                format_func=lambda v: t('filter_all') if v == "All" else status_label(v),
            )

        filtered = apps
        if search:
            filtered = [a for a in filtered if search.lower() in a.get('company', '').lower()
                       or search.lower() in a.get('position', '').lower()]
        if filter_status != "All":
            filtered = [a for a in filtered if a.get('status') == filter_status]

        for app in filtered:
            with st.expander(f"{app.get('company')} - {app.get('position')} ({status_label(app.get('status'))})"):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**{t('applied_on')}:** {app.get('date_applied')}")
                    st.write(f"**{t('status')}:** {status_label(app.get('status'))}")
                    if app.get('job_url'):
                        st.markdown(f"[{t('job_posting_link')}]({app['job_url']})")

                    if app.get('keywords'):
                        with st.expander(t('ai_analysis')):
                            st.markdown(app['keywords'])

                with col2:
                    new_status = st.selectbox(
                        t('update'),
                        STATUS_VALUES,
                        index=STATUS_VALUES.index(app.get('status', 'Applied')),
                        format_func=status_label,
                        key=f"s_{app['id']}"
                    )

                    if st.button(t('save'), key=f"save_{app['id']}"):
                        db.update_application(user_id, app['id'], {'status': new_status})
                        st.success(t('updated'))
                        st.rerun()

                    if st.button(t('delete'), key=f"del_{app['id']}"):
                        db.delete_application(user_id, app['id'])
                        st.success(t('deleted'))
                        st.rerun()

                if st.session_state.ai_available:
                    st.markdown("---")
                    st.markdown(f"**{t('ai_writing_tools')}**")
                    col_a, col_b, col_c = st.columns(3)

                    with col_a:
                        if st.button(t('generate_cover_letter'), key=f"cover_{app['id']}", use_container_width=True):
                            if not (profile and profile.get('resume')):
                                st.warning(t('add_resume_warning'))
                            elif not app.get('job_description'):
                                st.warning(t('no_jd_warning'))
                            else:
                                loading = show_ai_loading(
                                    [t('loading_reading_jd'), t('loading_drafting_letter')],
                                    show_skeleton=False,
                                )
                                letter = ai.generate_cover_letter(
                                    app.get('company', ''),
                                    app.get('position', ''),
                                    app.get('job_description', ''),
                                    profile.get('resume', ''),
                                    lang=st.session_state.lang,
                                )
                                loading.empty()
                                st.session_state[f'cover_letter_{app["id"]}'] = letter

                    with col_b:
                        if st.button(t('improve_resume'), key=f"resumetips_{app['id']}", use_container_width=True):
                            if not (profile and profile.get('resume')):
                                st.warning(t('add_resume_warning'))
                            elif not app.get('job_description'):
                                st.warning(t('no_jd_warning'))
                            else:
                                loading = show_ai_loading(
                                    [t('loading_comparing_role')],
                                    show_skeleton=False,
                                )
                                tips = ai.customize_resume(
                                    profile.get('resume', ''), app.get('job_description', ''),
                                    lang=st.session_state.lang,
                                )
                                loading.empty()
                                st.session_state[f'resume_tips_{app["id"]}'] = tips

                    with col_c:
                        if st.button(t('check_match_score'), key=f"matchscore_{app['id']}", use_container_width=True):
                            if not (profile and profile.get('resume')):
                                st.warning(t('add_resume_warning'))
                            elif not app.get('job_description'):
                                st.warning(t('no_jd_warning'))
                            else:
                                loading = show_ai_loading(
                                    [t('loading_scoring_resume')],
                                    show_skeleton=False,
                                )
                                match = ai.analyze_job_match(
                                    profile.get('resume', ''), app.get('job_description', ''),
                                    lang=st.session_state.lang,
                                )
                                loading.empty()
                                st.session_state[f'match_score_{app["id"]}'] = match

                    if f'cover_letter_{app["id"]}' in st.session_state:
                        st.markdown(f"#### {t('cover_letter_heading')}")
                        st.markdown(st.session_state[f'cover_letter_{app["id"]}'])

                    if f'resume_tips_{app["id"]}' in st.session_state:
                        st.markdown(f"#### {t('resume_suggestions_heading')}")
                        st.markdown(st.session_state[f'resume_tips_{app["id"]}'])

                    if f'match_score_{app["id"]}' in st.session_state:
                        st.markdown(f"#### {t('match_score_heading')}")
                        st.markdown(st.session_state[f'match_score_{app["id"]}'])

# ===== PORTFOLIO PAGE =====
elif page == "Portfolio":
    page_header(t('portfolio_page_title'), t('portfolio_page_sub'))

    projects = db.get_portfolio_projects(user_id)

    col1, col2, col3 = st.columns(3)
    col1.metric(t('portfolio_stat_projects'), len(projects))
    col2.metric(t('portfolio_stat_written'), len([p for p in projects if p.get('generated')]))
    col3.metric(t('portfolio_stat_drafts'), len([p for p in projects if not p.get('generated')]))

    st.markdown("---")

    with st.expander(t('add_new_project')):
        with st.form("new_project"):
            title = st.text_input(t('project_title'), placeholder="AI Job Search Platform")
            col1, col2 = st.columns(2)
            with col1:
                role = st.text_input(t('your_role'), placeholder="Full-stack developer")
            with col2:
                tech_stack = st.text_input(t('tech_stack'), placeholder="Python, Streamlit, Claude API, MongoDB")

            description = st.text_area(
                t('project_desc_label'),
                height=150,
                placeholder="Built a job search platform that uses Claude API to..."
            )
            outcome = st.text_area(
                t('project_outcome_label'),
                height=80,
                placeholder="Deployed and used daily; improved Lighthouse accessibility score from 88 to 94"
            )

            submit_project = st.form_submit_button(t('add_project'), type="primary", use_container_width=True)

            if submit_project:
                if title and description:
                    db.add_portfolio_project(user_id, {
                        'title': title,
                        'role': role,
                        'tech_stack': tech_stack,
                        'description': description,
                        'outcome': outcome,
                    })
                    success_check(t('added_company').format(name=title))
                    st.rerun()
                else:
                    st.error(t('title_desc_required'))

    st.markdown("---")

    if len(projects) == 0:
        st.info(t('no_projects_yet'))
    else:
        section_heading(t('projects_count').format(count=len(projects)))

        for project in projects:
            with st.expander(project.get('title', 'Untitled Project')):
                st.write(f"**{t('role_label')}:** {project.get('role') or 'N/A'}")
                st.write(f"**{t('tech_stack')}:** {project.get('tech_stack') or 'N/A'}")
                st.write(f"**{t('notes_label')}:** {project.get('description', 'N/A')}")
                if project.get('outcome'):
                    st.write(f"**{t('outcome_label')}:** {project.get('outcome')}")

                col_a, col_b = st.columns([1, 1])

                with col_a:
                    if not st.session_state.ai_available:
                        st.caption(t('ai_unavailable'))
                    else:
                        button_label = t('regenerate') if project.get('generated') else t('generate_portfolio_entry')
                        if st.button(button_label, key=f"genport_{project['id']}", type="primary", use_container_width=True):
                            loading = show_ai_loading([t('loading_writing_portfolio')], show_skeleton=False)
                            content = ai.generate_portfolio_content(project, lang=st.session_state.lang)
                            loading.empty()
                            db.update_portfolio_project(user_id, project['id'], {'generated': content})
                            st.rerun()

                with col_b:
                    if st.button(t('delete'), key=f"delport_{project['id']}", use_container_width=True):
                        db.delete_portfolio_project(user_id, project['id'])
                        st.rerun()

                if project.get('generated'):
                    st.markdown("---")
                    st.markdown(f"#### {t('portfolio_entry_heading')}")
                    st.markdown(project['generated'])

# ===== ANALYTICS PAGE =====
elif page == "Analytics":
    page_header(t('analytics_page_title'), t('analytics_page_sub'))

    apps = db.get_all_applications(user_id)
    stats = db.get_statistics(user_id)

    if len(apps) == 0:
        st.info(t('no_data_yet'))
    else:
        col1, col2 = st.columns(2)

        with col1:
            section_heading(t('status_distribution'))

            status_df = pd.DataFrame({
                "Status": [status_label(v) for v in STATUS_VALUES],
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
            section_heading(t('recent_activity'))

            status_color = {
                "Applied": "var(--accent)",
                "Interview": "var(--warning)",
                "Offer": "var(--success)",
                "Rejected": "var(--danger)",
            }

            # Keep this markup unindented — Markdown turns 4+ leading spaces
            # into a code block, which would print the tags instead of rendering.
            items = "".join(
                f'<div class="timeline-item" style="--dot-color: '
                f'{status_color.get(app.get("status"), "var(--accent)")}; --i:{i};">'
                f'<div class="t-title">{app["company"]} &mdash; {app["position"]}</div>'
                f'<div class="t-meta">{t("timeline_meta").format(status=status_label(app["status"]), date=app["date_applied"])}</div>'
                f'</div>'
                for i, app in enumerate(apps[:5])
            )

            st.markdown(f'<div class="timeline">{items}</div>', unsafe_allow_html=True)