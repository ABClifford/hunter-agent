"""Callback functions for tracing and logging."""

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest


# Track last known state to detect changes
last_state_snapshot = {}


def trace_callback(callback_context: CallbackContext, llm_request: LlmRequest):
    """Trace LLM calls and state changes with optimized logging."""
    global last_state_snapshot

    print("\n" + "="*80)
    print(f"AGENT: {callback_context.agent_name}")

    # Get user query from the last user message in contents
    user_query = "N/A"
    if llm_request.contents:
        for content in reversed(llm_request.contents):
            if content.role == "user":
                if content.parts and content.parts[0].text:
                    user_query = content.parts[0].text[:100]  # First 100 chars
                    break

    print(f"USER QUERY: {user_query}")
    print("-"*80)

    # Access current state
    current_state = callback_context.state

    # Check for job_history changes
    if "job_history" in current_state:
        current_job_history = str(current_state["job_history"])
        last_job_history = last_state_snapshot.get("job_history", "")

        if current_job_history != last_job_history:
            print("\n[STATE CHANGE] job_history updated:")
            print(f"{current_state['job_history']}")
            last_state_snapshot["job_history"] = current_job_history

    # Check for career_goals changes
    if "career_goals" in current_state:
        current_career_goals = str(current_state["career_goals"])
        last_career_goals = last_state_snapshot.get("career_goals", "")

        if current_career_goals != last_career_goals:
            print("\n[STATE CHANGE] career_goals updated:")
            print(f"{current_state['career_goals']}")
            last_state_snapshot["career_goals"] = current_career_goals

    print("="*80 + "\n")
