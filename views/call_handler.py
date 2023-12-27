from flask import Blueprint, url_for, request
from twilio.twiml.voice_response import VoiceResponse, Gather

from ..utils import twiml_response, return_home, goodbye, survey_instructions, Question

ivr_phone_tree = Blueprint("phone_tree", __name__)

QUESTIONS = [
    Question("Do you use Facebook?", "phone_tree.answer_handler", 1),
    Question("How often do you eat?", "phone_tree.answer_handler", 2),
    Question("Do you like to dance?", "phone_tree.answer_handler"),
]


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


@ivr_phone_tree.route("/questions/<int:question_index>", methods=["POST"])
def questions_handler(question_index):
    """Generic view function to handle questions"""
    res = VoiceResponse()

    if 0 <= question_index < len(QUESTIONS):
        current_question = QUESTIONS[question_index]

        gather = Gather(
            input="speech",
            action=url_for(
                current_question.handler,
                question_index=0
                if question_index == 0
                else current_question.next_question,
            ),
            method="POST",
        )
        gather.say(current_question.text)
        res.append(gather)

    else:
        return return_home()

    return twiml_response(res)


@ivr_phone_tree.route("/answers/<int:question_index>", methods=["POST"])
def answer_handler(question_index):
    """Handler for answers to questions"""
    res = VoiceResponse()

    if 0 <= question_index < len(QUESTIONS):
        current_question = QUESTIONS[question_index]
        transcribed_text = request.form["SpeechResult"]
        print(
            "Transcribed Text for question {}: {}".format(
                question_index, transcribed_text
            )
        )

        if current_question.next_question is not None:
            res.say("Next Question")
            res.redirect(
                url_for(
                    "phone_tree.questions_handler",
                    question_index=current_question.next_question,
                ),
                method="POST",
            )
        else:
            res.say("Thank you for completing the survey. Goodbye!")
            res.hangup()
    else:
        return return_home()

    return twiml_response(res)
