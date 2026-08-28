from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

class AIHelper:
    def __init__(self):
        """Initialize Claude AI client with API key"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file")
        self.client = Anthropic(api_key=api_key)
    
    def extract_keywords(self, job_description):
        """Extract key information from job description using AI"""
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": f"""Analyze this job description and extract:
                    1. Top 10 most important technical skills/keywords
                    2. Required years of experience
                    3. Top 3 key responsibilities
                    
                    Job Description:
                    {job_description}
                    
                    Format your response as:
                    **Skills:** skill1, skill2, skill3...
                    **Experience:** X years
                    **Key Responsibilities:**
                    - responsibility 1
                    - responsibility 2
                    - responsibility 3
                    """
                }]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error analyzing job description: {str(e)}"
    
    def customize_resume(self, resume, job_description):
        """Provide suggestions to customize resume for specific job"""
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                messages=[{
                    "role": "user",
                    "content": f"""Given this resume and job description, 
                    suggest 5 specific improvements to tailor the resume.
                    
                    Resume:
                    {resume}
                    
                    Job Description:
                    {job_description}
                    
                    Provide actionable, specific suggestions that will make 
                    this resume stand out for this particular job.
                    """
                }]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error generating suggestions: {str(e)}"
    
    def generate_cover_letter(self, company, position, 
                            job_description, resume):
        """Generate a professional cover letter"""
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                messages=[{
                    "role": "user",
                    "content": f"""Write a professional cover letter for:
                    Company: {company}
                    Position: {position}
                    
                    Job Description:
                    {job_description}
                    
                    My Resume:
                    {resume}
                    
                    Make it concise (3-4 paragraphs), genuine, and tailored 
                    to this specific role. Highlight relevant experience and 
                    express genuine interest in the company.
                    """
                }]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error generating cover letter: {str(e)}"
    
    def analyze_job_match(self, resume, job_description):
        """Analyze how well resume matches the job requirements"""
        try:
            message = self.client.messages.create(
                model="claude-sonnet-5",
                max_tokens=1536,
                messages=[{
                    "role": "user",
                    "content": f"""Analyze how well this resume matches the job requirements.
                    
                    Resume:
                    {resume}
                    
                    Job Description:
                    {job_description}
                    
                    Provide:
                    1. Match score (0-100%)
                    2. Strong matches (what aligns well)
                    3. Gaps (what's missing)
                    4. Top 3 recommendations to improve match
                    
                    Format as:
                    **Match Score:** XX%
                    **Strong Matches:**
                    - point 1
                    - point 2
                    **Gaps:**
                    - gap 1
                    - gap 2
                    **Recommendations:**
                    1. recommendation 1
                    2. recommendation 2
                    3. recommendation 3
                    """
                }]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error analyzing match: {str(e)}"
    
    def recommend_companies(self, profile):
        """Recommend companies based on user profile, grounded with live web search
        so posting status and culture notes reflect what was actually found online
        rather than the model's memorized guesses."""
        try:
            skills = ", ".join(profile.get('skills', []))
            education = profile.get('education', '')
            experience = profile.get('experience', '')
            target_location = profile.get('target_location', '')

            message = self.client.messages.create(
                model="claude-sonnet-5",
                max_tokens=7000,
                tools=[{
                    "type": "web_search_20260209",
                    "name": "web_search",
                    "max_uses": 8,
                }],
                messages=[{
                    "role": "user",
                    "content": f"""Based on this profile, recommend 12 companies that would be a good match.
Use web search to check each company's careers page or recent postings for a role
matching this profile, and to look up what the company says about its culture,
values, or ideal-candidate profile ("인재상" if Korean).

Profile:
- Education: {education}
- Skills: {skills}
- Experience: {experience}
- Target Location: {target_location}

For each company, provide:
1. Company name
2. Position type (e.g., Software Engineer, Data Scientist)
3. Match score (0-100%)
4. Why it's a good match
5. Requirements
6. What's missing from profile
7. Whether you found a real, current job posting or open careers listing for a
   matching role during your search
8. A short note on the company's stated culture/values, based only on what you
   found in search results

Be honest about verification: if you could not find a live posting or clear culture
information via search, say so explicitly instead of guessing or assuming one exists.

Format each company as:
---
**Company:** [name]
**Position:** [position]
**Match Score:** [score]%
**Why Good Match:** [reason]
**Requirements:** [requirements]
**Gaps:** [gaps]
**Posting Status:** [Found: <url> | Not confirmed]
**Culture Notes:** [notes based on search, or "Not confirmed via search"]
---

Focus on both Korean companies (Samsung, SK Hynix, Naver, Kakao, etc.) and global companies based on location preference.
"""
                }]
            )
            text_parts = [block.text for block in message.content if block.type == "text"]
            return "\n".join(text_parts) if text_parts else "No recommendations generated."
        except Exception as e:
            return f"Error generating recommendations: {str(e)}"
    
    def analyze_company_fit(self, profile, company_name, job_description):
        """Analyze detailed fit for a specific company"""
        try:
            skills = ", ".join(profile.get('skills', []))
            
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": f"""Analyze how well this candidate fits this specific job.

Candidate Profile:
- Education: {profile.get('education', '')}
- Skills: {skills}
- Experience: {profile.get('experience', '')}

Company: {company_name}
Job Description:
{job_description}

Provide:
1. Overall match score (0-100%)
2. Strong matches (skills/experience that align)
3. Gaps (what's missing)
4. Preparation roadmap (what to learn/build to improve fit)
5. Timeline estimate (how long to prepare)

Format as:
**Match Score:** XX%

**Strong Matches:**
- point 1
- point 2

**Gaps:**
- gap 1
- gap 2

**Preparation Roadmap:**
1. Learn/build X (estimated time: Y weeks)
2. Learn/build Z (estimated time: Y weeks)

**Recommended Timeline:** X weeks total
"""
                }]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error analyzing fit: {str(e)}"
    
    def generate_learning_roadmap(self, current_skills, target_skills):
        """Generate learning roadmap for missing skills"""
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": f"""Create a learning roadmap to acquire these skills.

Current Skills: {", ".join(current_skills)}
Target Skills Needed: {", ".join(target_skills)}

Provide:
1. Prioritized list of skills to learn
2. For each skill:
   - Best learning resources (courses, books, tutorials)
   - Estimated time to basic proficiency
   - Project ideas to practice
3. Total timeline

Format as:
**Priority 1: [Skill Name]**
- Resources: [list]
- Time needed: X weeks
- Practice project: [idea]

**Priority 2: [Skill Name]**
...

**Total Timeline:** X weeks
"""
                }]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error generating roadmap: {str(e)}"

    def strengthen_resume_for_company(self, resume, company_name, culture_notes=""):
        """Suggest resume wording that genuinely reflects a specific company's stated
        culture/values, grounded with live web search. Never invents new experience —
        only reorders or rewords what is already in the resume."""
        try:
            culture_hint = (
                f"\n\nNotes already gathered about this company's culture: {culture_notes}"
                if culture_notes and "Not confirmed" not in culture_notes else ""
            )
            message = self.client.messages.create(
                model="claude-sonnet-5",
                max_tokens=4000,
                tools=[{
                    "type": "web_search_20260209",
                    "name": "web_search",
                    "max_uses": 5,
                }],
                messages=[{
                    "role": "user",
                    "content": f"""Search for {company_name}'s stated company values, culture,
or ideal-candidate profile ("인재상" if Korean), then suggest how to reword or
reprioritize this resume so it genuinely reflects that alignment.

Resume:
{resume}
{culture_hint}

Provide:
**Company Values Found:** [what you found via search, or "Not confirmed via search" if nothing reliable turned up]
**Suggested Resume Adjustments:**
- [specific wording or reordering suggestion tied to an existing resume bullet]
- [specific wording or reordering suggestion tied to an existing resume bullet]
- [specific wording or reordering suggestion tied to an existing resume bullet]

Only suggest rewording or reprioritizing what is already true in the resume above.
Do not suggest adding experience, skills, or metrics that are not already there.
"""
                }]
            )
            text_parts = [block.text for block in message.content if block.type == "text"]
            return "\n".join(text_parts) if text_parts else "No suggestions generated."
        except Exception as e:
            return f"Error generating resume alignment suggestions: {str(e)}"

    def generate_portfolio_content(self, project):
        """Turn raw project notes into a polished portfolio write-up"""
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1536,
                messages=[{
                    "role": "user",
                    "content": f"""Turn these raw project notes into a polished portfolio entry.

Project Title: {project.get('title', '')}
Role: {project.get('role', '')}
Tech Stack: {project.get('tech_stack', '')}
Raw Description (what I did): {project.get('description', '')}
Outcome/Impact (if any): {project.get('outcome', '')}

Write a concise, achievement-oriented portfolio entry a recruiter would
find compelling. Do not invent facts, metrics, or outcomes that are not
implied by the notes above.

Format as:
**Summary:** [1-2 sentence hook describing what the project is and the problem it solves]
**Highlights:**
- [achievement/impact-oriented bullet 1]
- [achievement/impact-oriented bullet 2]
- [achievement/impact-oriented bullet 3]
**Tags:** [comma-separated tech/skill tags suitable for a portfolio site]
"""
                }]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error generating portfolio content: {str(e)}"