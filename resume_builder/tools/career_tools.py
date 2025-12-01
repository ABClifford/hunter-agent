"""Tools for career goals management."""

from typing import Annotated
from google.adk.tools.tool_context import ToolContext


def update_career_goals(
    tool_context: ToolContext,
    goal_type: str,
    details: str
) -> str:
    """Save career goals and aspirations information to session state.

    This tool stores insights gathered during career interviews, including career aspirations,
    values, interests, preferred work environments, and both short-term and long-term objectives.

    NOTE: This is agglutinative - multiple entries for the same goal_type are appended as a list,
    preserving all insights gathered over the course of the interview.

    Args:
        goal_type: The type of goal information (e.g., 'short_term', 'long_term', 'values', 'interests', 'preferences')
        details: The detailed information about this aspect of their career goals
    """
    try:
        # Initialize career_goals dict if it doesn't exist
        if "career_goals" not in tool_context.state:
            tool_context.state["career_goals"] = {}

        # Initialize as empty list if this is a new goal_type
        if goal_type not in tool_context.state["career_goals"]:
            tool_context.state["career_goals"][goal_type] = []

        # Append new details to the list (agglutinative behavior)
        tool_context.state["career_goals"][goal_type].append(details)

        print(f"Saved career goal - {goal_type}: {details}")
        print(f"  (Total entries for '{goal_type}': {len(tool_context.state['career_goals'][goal_type])})")
        return f"Successfully added to {goal_type} in career goals (total entries: {len(tool_context.state['career_goals'][goal_type])})."

    except Exception as e:
        print(f"Error saving career goals: {e}")
        return f"Error saving career goals: {str(e)}"
