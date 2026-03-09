# AI Job Search Platform

AI-powered job search and application management platform that helps job seekers find the best matching companies and prepare strategically.

## Features

- **AI Company Recommendations**: Get personalized company recommendations based on your profile
- **Match Analysis**: See how well you match with each company (match score, requirements, gaps)
- **Application Tracker**: Manage all your job applications in one place
- **Learning Roadmap**: Get AI-generated learning plans to fill skill gaps
- **Analytics**: Track your application progress with visual insights

## Tech Stack

- **Frontend**: Streamlit
- **AI**: Claude API (Anthropic)
- **Database**: MongoDB (with in-memory fallback)
- **Python**: 3.8+

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/job-search-platform.git
cd job-search-platform
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables

Create a `.env` file:
```
ANTHROPIC_API_KEY=your-api-key-here
MONGODB_URI=your-mongodb-uri (optional)
```

4. Run the application
```bash
streamlit run app.py
```

## Usage

1. **Profile Setup**: Enter your education, skills, and target positions
2. **Discover Jobs**: Get AI recommendations for companies that match your profile
3. **My Applications**: Track and manage your applications
4. **Analytics**: View your application statistics

## Project Structure
```
├── app.py              # Main Streamlit application
├── database.py         # Database operations (MongoDB/in-memory)
├── ai_helper.py        # AI/Claude API integration
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
```

## Author

Sunghoon Lee
- University of Wisconsin-Madison, B.S. Computer Science (Dec 2025)
- [LinkedIn](your-linkedin-url)
- [GitHub](https://github.com/yourusername)