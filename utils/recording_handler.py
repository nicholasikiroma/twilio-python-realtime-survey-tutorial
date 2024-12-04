from dataclasses import dataclass
from datetime import datetime
import os
from uuid import uuid4

from ..config import account_sid, auth_token


@dataclass
class RecordingHandler:
    base_recording_path = "recordings"
    os.makedirs(base_recording_path, exist_ok=True)

    def generate_session_id(self):
        """
        Generate a unique session identifier

        Returns:
            str: Unique session ID
        """
        return str(uuid4())

    def save_recording(self, recording_url, session_id=None):
        """
        Save recording from Twilio to local storage

        Args:
            recording_url (str): URL of the Twilio recording
            session_id (str, optional): Unique session identifier

        Returns:
            str: Path to saved recording
        """
        if not session_id:
            session_id = self.generate_session_id()

        try:
            # Fetch recording from Twilio
            import requests

            response = requests.get(
                recording_url, timeout=10, auth=(account_sid, auth_token)
            )
            response.raise_for_status()
            # Determine file extension
            content_type = response.headers.get("Content-Type", "audio/wav")
            extension = {
                "audio/wav": ".wav",
                "audio/mp3": ".mp3",
                "audio/mpeg": ".mp3",
            }.get(content_type, ".wav")

            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{session_id}_{timestamp}{extension}"
            filepath = os.path.join(self.base_recording_path, filename)

            # Save recording
            with open(filepath, "wb") as f:
                f.write(response.content)

            return filepath

        except Exception as e:
            print(f"Error saving recording: {e}")
            return None

    def store_recording_metadata(self, session_id, recording_path, survey_responses):
        """
        Store metadata about the recording and survey responses

        Args:
            session_id (str): Unique session identifier
            recording_path (str): Path to the saved recording
            survey_responses (dict): Responses collected during the survey

        Returns:
            dict: Metadata about the recording
        """
        metadata = {
            "session_id": session_id,
            "recording_path": recording_path,
            "timestamp": datetime.now().isoformat(),
            "responses": survey_responses,
        }

        # Optional: Store in database or JSON file
        metadata_path = os.path.join(
            self.base_recording_path, f"{session_id}_metadata.json"
        )

        import json

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        return metadata
