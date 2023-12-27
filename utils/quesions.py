"""Question class"""


class Question:
    def __init__(self, text, handler, next_question_index=None):
        self.text = text
        self.handler = handler
        self.next_question = next_question_index
