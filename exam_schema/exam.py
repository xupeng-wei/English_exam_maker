from pydantic import BaseModel
import enum


class QuestionType(enum.Enum):
    MCQ = "Multiple-Choice-Question"
    MC_READING = "Reading-Comprehension-With-Multiple-Choices"
    TF_READING = "Reading-Comprehension-With-True-or-False"
    MC_CLOZE = "Cloze-With-Multiple-Choices"
    FR_CLOZE = "Cloze-With-Free-Responses"
    # not to support other types for now

class Choices(BaseModel):
    A: str
    B: str
    C: str
    D: str

class Question(BaseModel):
    text: str
    choices: Choices
    answer: str
    is_answer_provided: bool
    explanation: str
    test_point: str

class QuestionSet(BaseModel):
    type: QuestionType
    context: str
    questions: list[Question]

class Exam(BaseModel):
    question_sets: list[QuestionSet]