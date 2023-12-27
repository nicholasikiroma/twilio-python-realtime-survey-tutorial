from flask import Response, url_for
from flask.testing import FlaskClient
from twilio.twiml.voice_response import VoiceResponse, Gather


def twiml_response(response):
    """Sets header of TwiML output"""
    res = Response(str(response))
    res.headers["Content-Type"] = "text/xml"
    return res


def return_home():
    """Takes user to the main menu"""
    res = VoiceResponse()
    res.say("Returning to the main menu", voice="Polly.Amy", language="en-US")
    res.redirect(url_for("phone_tree.root_menu"))
    return twiml_response(res)


def goodbye(response):
    response.say(
        "Thank you for calling SurveySprint " + "have a pleasant day",
        voice="Polly.Amy",
        language="en-US",
    )
    response.hangup()
    return response


def survey_instructions(response):
    response.say("Please say your answer after each question")
    response.redirect(
        url_for("phone_tree.questions_handler", question_index=0), method="POST"
    )
    return VoiceResponse()
