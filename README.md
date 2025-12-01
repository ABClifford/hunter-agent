# hunter-agent
Multiagent resume customizer, submitted for Kaggle Agents Intensive Capstone Project

# Resume Builder - AI Career Assistant

An AI-powered career assistant built with Google's Agent Development Kit (ADK) that helps job seekers by:
- Parsing resumes to extract structured career information
- Conducting detailed job history interviews
- Understanding career goals and aspirations
- Creating custom resumes for user-provided job listings.

## Features

- **Multi-agent architecture**: Specialized agents for different interview types
- **Resume parsing**: Automatic extraction of work history, education, skills, and more
- **Persistent sessions**: Database-backed conversation history
- **State management**: Maintains job history and career goals across conversations
- **Context injection**: Career interviewer receives relevant background automatically

## Project Structure
## Setup

1. **Create a virtual environment**:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
# Set your Google API key
set GOOGLE_API_KEY=your_api_key_here
```

4. **Prepare your resume**:
Place your resume PDF in the project directory and update `RESUME_FILE_PATH` in `resume_builder/config.py`.

## Usage

### Running the application

```bash
python main.py
```

This will:
1. Upload and parse your resume
2. Start an interactive session with the career coordinator
3. Store conversation history in a SQLite database

### Using in Jupyter notebooks

You can also use the agents interactively in Jupyter:

```python
import asyncio
from google.adk.apps.app import App
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService

from resume_builder.agents import (
    create_resume_interviewer,
    create_career_interviewer,
    create_coordinator,
)
from resume_builder.utils import run_session
from resume_builder.config import APP_NAME, DATABASE_URL

# Create agents
resume_interviewer = create_resume_interviewer()
career_interviewer = create_career_interviewer()
root_agent = create_coordinator(resume_interviewer, career_interviewer)

# Create app and runner
app = App(name=APP_NAME, root_agent=root_agent)
session_service = DatabaseSessionService(db_url=DATABASE_URL)
runner = Runner(app=app, session_service=session_service)

# Run a session
await run_session(
    runner_instance=runner,
    session_service=session_service,
    user_queries="Tell me about my work history",
    session_name="my-session"
)
```

## Configuration

Edit `resume_builder/config.py` to customize:
- `GOOGLE_API_KEY`: Your Google API key
- `MODEL_NAME`: The LLM model to use (default: "gemini-2.5-flash-lite")
- `DATABASE_URL`: Database connection string
- `RESUME_FILE_PATH`: Path to your resume PDF
- `RETRY_CONFIG`: HTTP retry options for API calls

## Architecture

### Agents

1. **Career Coordinator** (`career_coordinator`):
   - Root orchestrator agent
   - Manages workflow and delegates to specialized agents
   - Tools: `get_history_from_resume`, `get_job_history`

2. **Resume Interviewer** (`resume_interview_agent`):
   - Conducts detailed job history interviews
   - Tools: `update_job_history`

3. **Career Interviewer** (`career_interview_agent`):
   - Explores career goals and aspirations
   - Receives job history context automatically
   - Tools: `update_career_goals`

### Session State

The system maintains two main state objects:

- `state['job_history']`: Structured resume data (name, contact, work history, education, skills, publications, volunteering)
- `state['career_goals']`: Career aspirations organized by type (short_term, long_term, values, interests, preferences)

### Tools

- **get_history_from_resume**: Parses resume document and extracts structured data
- **get_job_history**: Retrieves formatted job history from session state
- **update_job_history**: Updates specific fields in job history
- **update_career_goals**: Saves career goal insights (agglutinative - appends to lists)

## Development

### Key Features

- **Context injection**: The career interviewer automatically receives job history context via `before_model_callback`
- **State change tracking**: Callbacks log state dumps only when changes occur
- **Date injection**: New sessions automatically receive current date context
- **Agglutinative career goals**: Multiple insights are appended as lists, preserving all gathered information

### Tracing

The system includes comprehensive tracing via `trace_callback`:
- Logs agent names and user queries
- Tracks state changes to `job_history` and `career_goals`
- Only shows full dumps when state actually changes

## Future Features

- 

## License

This project uses Google's Agent Development Kit. See ADK documentation for license details.


