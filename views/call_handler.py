from flask import Blueprint, url_for, request
from twilio.twiml.voice_response import VoiceResponse, Gather

from ..utils import twiml_response, return_home, goodbye, survey_instructions

ivr_phone_tree = Blueprint("phone_tree", __name__)


@ivr_phone_tree.route("/welcome", methods=["POST"])
def index():
    """welcome"""
    res = VoiceResponse()
    with res.gather(
        num_digits=1, action=url_for("phone_tree.root_menu"), method="POST"
    ) as responder:
        responder.say(
            message="Thank you for calling SurveySprint. "
            + "Kindly press 1 if you want to continue with the survey. "
            + "Press 2 if you will like to cancel. ",
            loop=3,
        )
    return twiml_response(res)


# handle root menu actions
@ivr_phone_tree.route("/ivr/menu", methods=["POST"])
def root_menu():
    """Main menu actions"""
    participant_choice = request.form["Digits"]
    actions = {"1": survey_instructions, "2": goodbye}
    if participant_choice in actions:
        res = VoiceResponse()
        actions[participant_choice](res)
        return twiml_response(res)

    return return_home()


@ivr_phone_tree.route("/questions/1", methods=["POST"])
def question_one():
    """Questions"""
    # How often do you use our products?
    res = VoiceResponse()
    with res.gather(
        input="speech", action=url_for("phone_tree.question_one_handler"), method="POST"
    ) as gather:
        gather.say(message="How often do you use Facebook?", voice="Polly.Ama", loop=2)

    res.append(gather)
    return twiml_response(res)


@ivr_phone_tree.route("/questions/handler", methods=["POST"])
def question_one_handler():
    """Handler for question one"""
    res = VoiceResponse()
    transcribed_text = request.form["SpeechResult"]
    print("Transcribed Text========>", transcribed_text)  # store response
    res.say("Next Question")
    res.redirect(url_for("phone_tree.question_two"), method="POST")
    return twiml_response(res)


@ivr_phone_tree.route("/questions/2", methods=["POST"])
def question_two():
    """Questions"""
    # Which features are most valuable to you
    res = VoiceResponse()
    res.say("Thank you for calling")
    res.hangup()
    return twiml_response(res)


@ivr_phone_tree.route("/questions/3", methods=["POST"])
def question_three():
    """Questions"""
    # How would you compare our products to our competitors’?
    return
