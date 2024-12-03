from .quesions import Question


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
        return self.questions[self.current_question_index] if self.questions else None
