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
                model="claude-sonnet-4-5-20250929",
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
        """Recommend companies based on user profile"""
        try:
            skills = ", ".join(profile.get('skills', []))
            education = profile.get('education', '')
            experience = profile.get('experience', '')
            target_location = profile.get('target_location', '')
            
            message = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=3000,
                messages=[{
                    "role": "user",
                    "content": f"""Based on this profile, recommend 10 companies that would be a good match.

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

Format each company as:
---
**Company:** [name]
**Position:** [position]
**Match Score:** [score]%
**Why Good Match:** [reason]
**Requirements:** [requirements]
**Gaps:** [gaps]
---

Focus on both Korean companies (Samsung, SK Hynix, Naver, Kakao, etc.) and global companies based on location preference.
"""
                }]
            )
            return message.content[0].text
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