"""Session management utilities."""

from datetime import datetime
from google.genai import types
from google.adk.runners import Runner

from ..config import USER_ID, MODEL_NAME

# Track which sessions have had date context injected
sessions_with_date = set()


async def run_session(
    runner_instance: Runner,
    session_service,
    user_queries: list[str | types.Content] | str | types.Content = None,
    session_name: str = "default",
):
    """Execute a session with the agent, processing user queries."""
    global sessions_with_date

    print(f"\n ### Session: {session_name}")

    app_name = runner_instance.app_name

    # Get existing session or create new one
    session = None
    is_new_session = False
    try:
        session = await session_service.get_session(
            app_name=app_name, user_id=USER_ID, session_id=session_name
        )
        if session is not None:
            print(f"[run_session] Retrieved existing session '{session_name}'")
    except Exception:
        pass  # Will create new session below

    # If we didn't get a session, create a new one
    if session is None:
        session = await session_service.create_session(
            app_name=app_name, user_id=USER_ID, session_id=session_name
        )
        print(f"[run_session] Created new session '{session_name}'")
        is_new_session = True

    # Process queries if provided
    if user_queries:
        # Convert single query to list for uniform processing
        if isinstance(user_queries, (str, types.Content)):
            user_queries = [user_queries]

        # For new sessions, prepend date context to the first query
        if is_new_session and session_name not in sessions_with_date:
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            date_context = f"[Today's date: {current_date}]\n\n"

            # Add date to first query
            first_query = user_queries[0]
            if isinstance(first_query, str):
                user_queries[0] = date_context + first_query
            else:
                # It's a Content object, prepend to first text part
                if hasattr(first_query, 'parts') and first_query.parts:
                    for part in first_query.parts:
                        if hasattr(part, 'text') and part.text:
                            part.text = date_context + part.text
                            break

            sessions_with_date.add(session_name)
            print(f"[run_session] Added date context: {current_date}")

        # Process each query in the list sequentially
        for query in user_queries:
            print(f"\nUser > {query if isinstance(query, str) else 'Content with file'}")

            # Convert string queries to ADK Content format, leave Content objects as-is
            if isinstance(query, str):
                query = types.Content(role="user", parts=[types.Part(text=query)])

            # Stream the agent's response asynchronously
            async for event in runner_instance.run_async(
                user_id=USER_ID, session_id=session.id, new_message=query
            ):
                # Check if the event contains valid content
                if event.content and event.content.parts:
                    # Handle all parts in the response
                    for part in event.content.parts:
                        # Handle text parts
                        if part.text and part.text != "None":
                            print(f"{MODEL_NAME} > ", part.text)
                        # Handle function calls (agent delegation)
                        elif hasattr(part, 'function_call') and part.function_call:
                            print(f"{MODEL_NAME} > [Calling function: {part.function_call.name}]")
                        # Handle function responses
                        elif hasattr(part, 'function_response') and part.function_response:
                            print(f"{MODEL_NAME} > [Function response received]")
    else:
        print("No queries!")
