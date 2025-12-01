"""File upload utilities."""

from google import genai


def upload_resume(file_path: str):
    """Upload a resume file to Google GenAI and return the file reference."""
    try:
        client = genai.Client()
        uploaded_file = client.files.upload(file=file_path)
        print(f"Uploaded file: {uploaded_file.name}")
        print(f"File URI: {uploaded_file.uri}")
        return uploaded_file
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None
