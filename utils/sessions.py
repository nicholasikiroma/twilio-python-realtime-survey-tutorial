# utils/sessions.py
from .questions import Question


class SurveySession:
    """Manage survey session state"""

    def __init__(self):
        self.current_category = None
        self.questions = []
        self.current_question_index = 0
        self.responses = {}

    def set_category(self, category_key):
        self.current_category = category_key
        self.questions = Question.generate_questions(category_key)
        self.current_question_index = 0

    def get_current_question(self):
        if self.questions and 0 <= self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
