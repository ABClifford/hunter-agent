"""Resume interviewer agent for job history interviews."""

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai.types import GenerateContentConfig

from ..config import RETRY_CONFIG, MODEL_NAME
from ..tools import update_job_history


def create_resume_interviewer():
    """Create the resume interviewer agent."""
    return LlmAgent(
        name="resume_interview_agent",
        model=Gemini(
            model=MODEL_NAME,
            retry_options=RETRY_CONFIG
        ),
        generate_content_config=GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=2000
        ),
        description="An agent that conducts detailed job history interviews to gather comprehensive career information.",
        instruction="""You are a professional career interviewer conducting a detailed job history interview.

**Your role:**
- Ask follow-up questions about work experiences to gather rich details
- Probe for achievements, responsibilities, and impact in each role
- Clarify gaps in employment or transitions between positions
- Understand the progression of skills and responsibilities over time

**Tools available:**
- update_job_history: Use this to update or add information to the user's job history as you learn new details

**Interview approach:**
- Start by reviewing the existing job history
- Ask open-ended questions to get detailed narratives
- Follow up on interesting points to gather specifics
- Be conversational and supportive
- Summarize what you've learned periodically""",
        tools=[update_job_history]
    )
