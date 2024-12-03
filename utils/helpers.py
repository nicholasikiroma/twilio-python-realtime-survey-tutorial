from flask import Response, url_for
from twilio.twiml.voice_response import VoiceResponse


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

    # Optional: Add more robust call termination
    res.pause(length=1)
    res.hangup()

    # Attempt to stop recording
    res.record(
        "",
        action=url_for("phone_tree.stop_recording"),
        method="POST",
        trim="trim-silence",
    )

    return res


def start_call_recording() -> Response:
    """
    Initiates call recording

    Returns:
        Response: TwiML response for starting recording
    """
    res = VoiceResponse()
    res.redirect(url_for("phone_tree.record"), method="POST")
    return twiml_response(res)


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
