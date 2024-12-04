from flask import Blueprint, url_for, request
from twilio.twiml.voice_response import VoiceResponse, Gather


from ..utils import (
    twiml_response,
    goodbye,
    start_call_recording,
    SurveySession,
    RecordingHandler,
    process_survey_results,
)

ivr_phone_tree = Blueprint("phone_tree", __name__)


# Global session storage (consider using Redis or database in a production environment)
survey_sessions = {}


@ivr_phone_tree.route("/welcome", methods=["POST"])
def index():
    """Welcome message with category selection"""
    res = VoiceResponse()

    # Create gather with category options
    gather = Gather(
        num_digits=1,
        action=url_for("phone_tree.category_selection"),
        method="POST",
    )

    gather.say(
        "Welcome to our interactive survey. "
        "Press 1 for Customer Satisfaction, "
        "Press 2 for Product Feedback, "
        "Press 3 for Employee Experience. "
        "Press 0 to exit."
    )

    res.append(gather)
    return twiml_response(res)


@ivr_phone_tree.route("/category", methods=["POST"])
def category_selection():
    """Handle category selection"""
    res = VoiceResponse()

    # Get caller's phone number as session identifier
    call_sid = request.form.get("CallSid")

    # Map input to category
    category_map = {
        "1": "customer_satisfaction",
        "2": "product_feedback",
        "3": "employee_experience",
    }

    participant_choice = request.form["Digits"]

    if participant_choice == "0":
        return goodbye(res)

    category_key = category_map.get(participant_choice)

    if not category_key:
        res.say("Invalid selection. Returning to main menu.")
        res.redirect(url_for("phone_tree.index"), method="POST")
        return twiml_response(res)

    # Create or update session
    session = SurveySession()
    session.set_category(category_key)
    survey_sessions[call_sid] = session

    res.redirect(url_for("phone_tree.start_recording"), method="POST")

    return twiml_response(res)


@ivr_phone_tree.route("/questions", methods=["POST"])
def questions_handler():
    """Handle survey questions dynamically"""
    res = VoiceResponse()

    # Retrieve session
    call_sid = request.form.get("CallSid") or request.args.get("CallSid")
    session = survey_sessions.get(call_sid)

    if not session:
        res.say("Session expired. Starting over.")
        res.redirect(url_for("phone_tree.index"), method="POST")
        return twiml_response(res)

    current_question = session.get_current_question()

    if not current_question:
        res.say("Survey completed. Thank you!")
        goodbye(res)
        return twiml_response(res)

    # Create gather for speech input
    gather = Gather(
        input="speech",
        action=url_for("phone_tree.answer_handler", CallSid=call_sid),
        method="POST",
    )

    gather.say(current_question.text)
    res.append(gather)

    return twiml_response(res)


@ivr_phone_tree.route("/answers", methods=["POST"])
def answer_handler():
    """Handle and confirm answers"""
    res = VoiceResponse()
    call_sid = request.form.get("CallSid") or request.args.get("CallSid")
    session = survey_sessions.get(call_sid)

    if not session:
        res.say("Session expired. Restarting.")
        res.redirect(url_for("phone_tree.index"), method="POST")
        return twiml_response(res)

    current_question = session.get_current_question()

    if "SpeechResult" in request.form:
        transcribed_text = request.form["SpeechResult"]

        # Store response
        session.responses[current_question.text] = transcribed_text

        # Confirm response
        gather = Gather(
            num_digits=1,
            action=url_for("phone_tree.confirmation_handler", CallSid=call_sid),
            method="POST",
        )

        gather.say(
            f"You said: {transcribed_text}. " "Press 1 to confirm, 2 to re-record."
        )

        res.append(gather)
    else:
        res.say("Sorry, we couldn't understand your response.")
        res.redirect(
            url_for("phone_tree.questions_handler", CallSid=call_sid),
            method="POST",
        )

    return twiml_response(res)


@ivr_phone_tree.route("/confirm", methods=["POST"])
def confirmation_handler():
    """Confirm or re-record response"""
    res = VoiceResponse()
    call_sid = request.form.get("CallSid") or request.args.get("CallSid")
    session = survey_sessions.get(call_sid)

    if not session:
        res.say("Session expired. Restarting.")
        res.redirect(url_for("phone_tree.index"), method="POST")
        return twiml_response(res)

    confirmation = request.form.get("Digits")

    if confirmation == "1":
        # Move to next question
        session.current_question_index += 1
        res.redirect(url_for("phone_tree.questions_handler"), method="POST")
    elif confirmation == "2":
        # Re-record current question
        res.redirect(url_for("phone_tree.questions_handler"), method="POST")
    else:
        res.say("Invalid input. Please try again.")
        res.redirect(url_for("phone_tree.confirmation_handler"), method="POST")

    return twiml_response(res)


@ivr_phone_tree.route("/start-recording", methods=["POST"])
def start_recording():
    """
    Initiate call recording and redirect to the questions handler.
    """
    res = VoiceResponse()
    call_sid = request.form.get("CallSid")

    res.say("Please note that the call will be recorded.")

    start_call_recording(call_sid=call_sid)

    res.say("The call is now being recorded.")

    # Redirect to the questions handler
    res.redirect(
        url_for("phone_tree.questions_handler", CallSid=call_sid), method="POST"
    )

    return twiml_response(res)


@ivr_phone_tree.route("stop-recording", methods=["GET"])
def stop_recording():
    """
    Twilio route to handle recording storage
    """
    recording_handler = RecordingHandler()

    # Get recording URL from Twilio
    recording_url = request.args.get("RecordingUrl")
    session_id = request.form.get("CallSid") or request.args.get("CallSid")

    # Retrieve survey session data
    survey_session = survey_sessions.get(session_id, {})

    if recording_url:
        # Save recording
        recording_path = recording_handler.save_recording(recording_url, session_id)

        # Store metadata
        recording_handler.store_recording_metadata(
            session_id, recording_path, survey_session.responses
        )

    process_survey_results(survey_session)

    return twiml_response(VoiceResponse())
