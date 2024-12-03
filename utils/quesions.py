from dataclasses import dataclass
from typing import List, Optional


@dataclass
class QuestionCategory:
    name: str
    questions: List[str]
    description: Optional[str] = None


SURVEY_CATEGORIES = {
    "customer_satisfaction": QuestionCategory(
        name="Customer Satisfaction",
        description="Gather insights about customer experience",
        questions=[
            "On a scale of 1 to 5, how satisfied are you with our service?",
            "Would you recommend our product to a friend or colleague?",
            "What is one thing we could improve about our service?",
        ],
    ),
    "product_feedback": QuestionCategory(
        name="Product Feedback",
        description="Collect detailed product usage insights",
        questions=[
            "How frequently do you use our product?",
            "What features do you find most valuable?",
            "Are there any features you wish we would add?",
        ],
    ),
    "employee_experience": QuestionCategory(
        name="Employee Experience",
        description="Understand workplace satisfaction and engagement",
        questions=[
            "How supported do you feel in your current role?",
            "Do you see opportunities for growth in our organization?",
            "What would make your work experience better?",
        ],
    ),
}


@dataclass
class Question:
    text: str
    handler: str
    next_question_index: Optional[int] = None
    category: Optional[str] = None

    @classmethod
    def generate_questions(cls, category_key: str) -> List["Question"]:
        """
        Generate a list of Question objects for a specific category
        """
        category = SURVEY_CATEGORIES.get(category_key)
        if not category:
            return []

        questions = []
        for i, question_text in enumerate(category.questions):
            next_index = i + 1 if i < len(category.questions) - 1 else None
            questions.append(
                cls(
                    text=question_text,
                    handler="phone_tree.answer_handler",
                    next_question_index=next_index,
                    category=category_key,
                )
            )

        return questions
