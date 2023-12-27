from flask import Response, url_for, redirect
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
    return question_one(response)


def question_one(response):
    gather = Gather(
        input="speech", action=url_for("phone_tree.question_one_handler"), method="POST"
    )
    gather.say("Do you use facebook?")
    response.append(gather)
    response.say("We didn't receive any input. Goodbye!")
    response.append(gather)
    return twiml_response(response)
