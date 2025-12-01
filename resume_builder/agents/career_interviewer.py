"""Career interviewer agent for career goals interviews."""

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.genai.types import GenerateContentConfig

from ..config import RETRY_CONFIG, MODEL_NAME
from ..tools import update_career_goals


def career_context_injection(callback_context: CallbackContext, llm_request: LlmRequest):
    """Inject job history context into the career interviewer's LLM request."""
    if "job_history" in callback_context.state:
        job_history = callback_context.state["job_history"]

        # Format job history as readable text
        context_parts = []

        if job_history.get('name'):
            context_parts.append(f"Candidate: {job_history['name']}")

        if job_history.get('work_history'):
            context_parts.append(f"\nWork History ({len(job_history['work_history'])} positions):")
            for i, job in enumerate(job_history['work_history'][:5], 1):
                job_info = f"{i}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')} ({job.get('dates', 'N/A')})"
                context_parts.append(job_info)

        if job_history.get('skills'):
            skills_preview = ', '.join(job_history['skills'][:10])
            context_parts.append(f"\nKey Skills: {skills_preview}")

        # Prepend to the system instruction
        context_text = "\n".join(context_parts)
        injection = f"[CONTEXT - Candidate Background]\n{context_text}\n\n[END CONTEXT]\n\n"
        llm_request.system_instruction = injection + (llm_request.system_instruction or "")


def create_career_interviewer():
    """Create the career interviewer agent."""
    return LlmAgent(
        name="career_interview_agent",
        model=Gemini(
            model=MODEL_NAME,
            retry_options=RETRY_CONFIG
        ),
        generate_content_config=GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=2000
        ),
        description="An agent that conducts in-depth career goals interviews to understand aspirations and preferences.",
        instruction="""You are a professional career counselor conducting a career goals interview.

**Your role:**
- Understand the candidate's short-term and long-term career aspirations
- Explore their values, interests, and work preferences
- Identify what motivates them and what kind of work environment they thrive in
- Help them articulate their career vision

**Tools available:**
- update_career_goals: Use this to save insights about their career goals, values, interests, and preferences

**Interview approach:**
- Ask thoughtful, open-ended questions
- Listen actively and probe deeper based on their responses
- Help them connect their past experiences to future aspirations
- Be encouraging and supportive
- Save insights frequently using the update_career_goals tool with appropriate goal_type categories:
  - 'short_term' for immediate career objectives (1-2 years)
  - 'long_term' for future aspirations (3-5+ years)
  - 'values' for what's important to them in work
  - 'interests' for topics/domains they're passionate about
  - 'preferences' for work environment, culture, role characteristics

**Example goal_types:**
- short_term: "Wants to transition into a senior engineering role within 18 months"
- long_term: "Aspires to become a CTO of a mid-sized tech company"
- values: "Prioritizes work-life balance and continuous learning opportunities"
- interests: "Passionate about AI/ML and sustainable technology"
- preferences: "Prefers remote-first companies with collaborative cultures"

Remember: The candidate's background information will be provided to you automatically. Use it to ask relevant follow-up questions.""",
        tools=[update_career_goals],
        before_model_callback=career_context_injection
    )
