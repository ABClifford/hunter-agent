"""Tools for resume parsing and job history management."""

import os
from typing import Annotated

from google import genai
from google.genai import types
from google.adk.tools.tool_context import ToolContext

from ..models import ResumeProcessing


def get_history_from_resume(
    tool_context: ToolContext,
    file_uri: str
) -> str:
    """Parse a resume file and extract structured information, saving it to session state.

    This tool analyzes a resume PDF and extracts structured data including name, contact info,
    work history, education, skills, publications, and volunteering experience.

    Args:
        file_uri: The URI of the uploaded resume file (e.g., 'files/abc123')
    """
    try:
        print(f"Tool called with file_uri: {file_uri}")

        # Create a client for the LLM call with API key from environment
        client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

        # Make a direct LLM call with structured output
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part(text="Extract all information from this resume document and return it in structured format."),
                        types.Part(file_data=types.FileData(file_uri=file_uri))
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=8000,
                response_mime_type="application/json",
                response_schema=ResumeProcessing
            )
        )

        # Parse the JSON response into the Pydantic model
        parsed_data = ResumeProcessing.model_validate_json(response.text)

        # Store in session state under 'job_history'
        tool_context.state["job_history"] = parsed_data.model_dump()

        print(f"Parsed resume data: {parsed_data.model_dump()}")
        return f"Successfully parsed resume for {parsed_data.name}. Data saved to session state under 'job_history'."

    except Exception as e:
        print(f"Error parsing resume: {e}")
        return f"Error parsing resume: {str(e)}"


def get_job_history(tool_context: ToolContext) -> str:
    """Retrieve the complete job history from session state.

    This tool returns all parsed resume data including name, contact info, work experience,
    education, skills, publications, and volunteering. Use this to access the user's
    background information when conducting interviews or providing advice.

    Returns a formatted summary of the resume data that's easy for the LLM to parse.
    """
    try:
        print("[get_job_history] Tool called - retrieving job history from state")

        # Check if job_history exists in state
        if "job_history" not in tool_context.state:
            print("[get_job_history] No job history found in state")
            return "No job history available. The resume hasn't been parsed yet. Please ask the user to provide their resume first."

        # Get the job history data
        job_history = tool_context.state["job_history"]
        print(f"[get_job_history] Retrieved job history for: {job_history.get('name', 'Unknown')}")

        # Create a more readable summary instead of raw JSON
        summary_parts = []

        # Basic info - only include if present
        if job_history.get('name'):
            summary_parts.append(f"Name: {job_history['name']}")
        if job_history.get('phone'):
            summary_parts.append(f"Contact: {job_history['phone']}")
        if job_history.get('address'):
            summary_parts.append(f"Location: {job_history['address']}")

        # Work history
        if job_history.get('work_history'):
            summary_parts.append(f"\nWork History ({len(job_history['work_history'])} positions):")
            for i, job in enumerate(job_history['work_history'][:5], 1):
                title = job.get('title', '')
                company = job.get('company', '')
                dates = job.get('dates', '')

                job_parts = []
                if title:
                    job_parts.append(title)
                if company:
                    job_parts.append(f"at {company}")
                if dates:
                    job_parts.append(f"({dates})")

                if job_parts:
                    summary_parts.append(f"{i}. {' '.join(job_parts)}")

                if job.get('description'):
                    desc = job['description'][:200] + "..." if len(job['description']) > 200 else job['description']
                    summary_parts.append(f"   {desc}")

        # Education
        if job_history.get('education'):
            summary_parts.append(f"\nEducation ({len(job_history['education'])} entries):")
            for i, edu in enumerate(job_history['education'], 1):
                institution = edu.get('institution', '')
                field = edu.get('field_of_study', '')
                dates = edu.get('dates', '')

                edu_parts = []
                if institution:
                    edu_parts.append(institution)
                if field:
                    edu_parts.append(f"- {field}")
                if dates:
                    edu_parts.append(f"({dates})")

                if edu_parts:
                    summary_parts.append(f"{i}. {' '.join(edu_parts)}")

        # Skills
        if job_history.get('skills'):
            skills_list = job_history['skills'][:10]
            summary_parts.append(f"\nKey Skills ({len(job_history['skills'])} total):")
            summary_parts.append(", ".join(skills_list))

        # Publications (if present)
        if job_history.get('publications'):
            summary_parts.append(f"\nPublications ({len(job_history['publications'])} entries):")
            for i, pub in enumerate(job_history['publications'][:3], 1):
                org = pub.get('organization', '')
                dates = pub.get('dates', '')
                desc = pub.get('description', '')

                pub_parts = []
                if org:
                    pub_parts.append(org)
                if dates:
                    pub_parts.append(f"({dates})")

                if pub_parts:
                    summary_parts.append(f"{i}. {' '.join(pub_parts)}")
                if desc:
                    summary_parts.append(f"   {desc[:150]}...")

        # Volunteering (if present)
        if job_history.get('volunteering'):
            summary_parts.append(f"\nVolunteering ({len(job_history['volunteering'])} entries):")
            for i, vol in enumerate(job_history['volunteering'][:3], 1):
                title = vol.get('title', '')
                company = vol.get('company', '')
                dates = vol.get('dates', '')

                vol_parts = []
                if title:
                    vol_parts.append(title)
                if company:
                    vol_parts.append(f"at {company}")
                if dates:
                    vol_parts.append(f"({dates})")

                if vol_parts:
                    summary_parts.append(f"{i}. {' '.join(vol_parts)}")

        result = "\n".join(summary_parts)
        print(f"[get_job_history] Returning summary ({len(result)} characters)")

        return result

    except Exception as e:
        error_msg = f"Error retrieving job history: {str(e)}"
        print(f"[get_job_history] {error_msg}")
        return error_msg


def update_job_history(
    tool_context: ToolContext,
    field: str,
    value: str
) -> str:
    """Update or modify job history information in session state.

    This tool allows updating any field in the parsed resume data, such as contact info,
    skills, work history, education, etc. Useful for correcting or adding information.

    Args:
        field: The field to update (e.g., 'name', 'phone', 'address', 'skills', 'work_history', 'education', 'introduction', 'publications', 'volunteering')
        value: The new value for this field (use JSON string for complex objects like work_history)
    """
    try:
        import json

        # Initialize job_history dict if it doesn't exist
        if "job_history" not in tool_context.state:
            tool_context.state["job_history"] = {}

        # Try to parse value as JSON for complex objects
        # If it fails, store as-is (for simple strings)
        try:
            parsed_value = json.loads(value)
            tool_context.state["job_history"][field] = parsed_value
            print(f"Updated job history - {field}: {parsed_value} (parsed from JSON)")
        except (json.JSONDecodeError, TypeError):
            # Not JSON, store as string
            tool_context.state["job_history"][field] = value
            print(f"Updated job history - {field}: {value} (stored as string)")

        return f"Successfully updated {field} in job history."

    except Exception as e:
        print(f"Error updating job history: {e}")
        return f"Error updating job history: {str(e)}"
