from pydantic import BaseModel
from typing import List


class QuizCreate(BaseModel):
    title: str
    description: str


class QuizQuestionCreate(BaseModel):
    question: str
    correct_answer: str
    answers: List[str]