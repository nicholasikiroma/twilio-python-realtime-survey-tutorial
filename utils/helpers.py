from flask import Response, url_for
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client

from ..config import account_sid, auth_token


def twiml_response(response: VoiceResponse) -> Response:
    """
    Sets header of TwiML output for Twilio voice response

    Args:
        response (VoiceResponse): Twilio voice response object

    Returns:
        Response: Flask response with XML content type
    """
    try:
        res = Response(str(response))
        res.headers["Content-Type"] = "text/xml"
        return res
    except Exception as e:
        print(f"Error creating TwiML response: {e}")
        # Fallback response
        fallback_res = VoiceResponse()
        fallback_res.say("Sorry, there was a system error.")
        return twiml_response(fallback_res)


def goodbye(res: VoiceResponse) -> VoiceResponse:
    """
    Gracefully ends survey and stops recording the call

    Args:
        res (VoiceResponse): Twilio voice response object

    Returns:
        VoiceResponse: Updated voice response with goodbye message
    """
    res.say(
        "Thank you for completing the survey. Have a pleasant day.",
    )

    res.pause(length=1)
    res.hangup()

    return res


def start_call_recording(call_sid: str):
    """
    Initiates call recording

    Returns:
        Response: Call context
    """
    try:
        client = Client(account_sid, auth_token)

        ongoing_call = client.calls(call_sid)

        recording = ongoing_call.recordings.create(
            recording_status_callback_event="completed",
            recording_status_callback=url_for(
                "phone_tree.stop_recording", _external=True
            ),
            recording_status_callback_method="GET",
        )
        return recording

    except Exception as e:
        print(f"Error creating recording instance: {e}")
        # Fallback response
        fallback_res = VoiceResponse()
        fallback_res.say("Sorry, there was a system error.")
        fallback_res.hangup()
        return fallback_res


def return_home() -> Response:
    """
    Handles unexpected scenarios by redirecting to welcome page

    Returns:
        Response: TwiML response redirecting to welcome route
    """
    res = VoiceResponse()
    res.say("Sorry, something went wrong. Returning to main menu.")
    res.redirect(url_for("phone_tree.index"), method="POST")
    return twiml_response(res)


def process_survey_results(session):
    """
    Optional method to process and store survey results
    In a real-world scenario, this would integrate with a database
    """
    print(f"Survey Category: {session.current_category}")
    for question, response in session.responses.items():
        print(f"Q: {question}\nA: {response}\n")
