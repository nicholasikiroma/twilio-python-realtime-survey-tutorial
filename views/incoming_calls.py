from flask import Blueprint, url_for
from twilio.twiml.voice_response import VoiceResponse

ivr_phone_tree = Blueprint("phone_tree", __name__)


@ivr_phone_tree.route("/welcome")
def index():
    """welcome"""
    res = VoiceResponse()
    with res.gather(num_digits=1, action=url_for("menu"), method="POST") as responder:
        responder.say(
            message="Thank you for calling SurveySprint. "
            + "Kindly press 1 if you want to continue with the survey."
            + "Press 2 if you will like to cancel.",
            loop=3,
        )
    return None
