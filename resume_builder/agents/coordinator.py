"""Root coordinator agent for orchestrating the resume builder system."""

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai.types import GenerateContentConfig

from ..config import RETRY_CONFIG, MODEL_NAME
from ..tools import get_history_from_resume, get_job_history
from ..utils import trace_callback


def create_coordinator(resume_interviewer, career_interviewer):
    """Create the root coordinator agent.

    Args:
        resume_interviewer: The resume interviewer agent instance
        career_interviewer: The career interviewer agent instance

    Returns:
        LlmAgent: The configured coordinator agent
    """
    return LlmAgent(
        name="career_coordinator",
        model=Gemini(
            model=MODEL_NAME,
            retry_options=RETRY_CONFIG
        ),
        generate_content_config=GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=2000
        ),
        description="A helpful career assistant that gathers job-seeker information and provides job recommendations.",
        instruction=f"""You are the system that connects job-seekers with personalized job recommendations.

**Your workflow:**
1. First, offer to help the user upload their resume using get_history_from_resume
2. If no resume is available, transfer to resume_interview_agent
3. Once the resume is parsed, you can transfer to specialized agents or retrieve job history as needed
4. Have subagents conduct interviews to understand their career goals and aspirations
5. Eventually, you'll provide personalized job recommendations (future feature)

**Components:**
1. get_history_from_resume: Use this tool to parse the user's uploaded resume file and extract structured job history data.
2. get_job_history: Use this tool to retrieve and display the user's job history from state.
3. resume_interview_agent: Transfer to this agent to conduct a detailed job history interview. This agent can update job history information as needed.
4. career_interview_agent: Transfer to this agent to conduct a detailed career goals interview; NEVER transfer to this agent until a state['job_history'] exists.

**Important rules:**
- Always parse the resume FIRST before conducting interviews
- Only transfer to career_interview_agent AFTER job history exists in state
- The resume_interview_agent can update job history details
- The career_interview_agent will save career goals to state['career_goals']

**Conversation style:**
- Be professional but friendly
- Guide users through the process step-by-step
- Explain what information you're gathering and why
- Summarize what you've learned periodically""",
        tools=[get_history_from_resume, get_job_history],
        sub_agents=[resume_interviewer, career_interviewer],
        before_model_callback=trace_callback
    )
