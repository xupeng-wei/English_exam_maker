from google import genai
from pydantic import BaseModel
import enum
import os

import logging
import time

from typing import Type, Optional

import sys
sys.path.append("..")
from exam_schema.exam import Exam, QuestionSet, Question, Choices, QuestionType

logging.basicConfig(
    level=logging.INFO,  # Set logging level (INFO, ERROR, DEBUG, etc.)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Add timestamp
    datefmt="%Y-%m-%d %H:%M:%S",  # Customize timestamp format
    force=True,
)

with open("google_gemini_key", "r") as f:
    GEMINI_API_KEY = f.read().strip() # Your GEMINI API key here
    if GEMINI_API_KEY == "":
        logging.fatal("GEMINI_API_KEY is empty")
        raise Exception("GEMINI_API empty")
    
def GeminiRequestWrapper(prompt: str, schema: Type[BaseModel], *args, **kwargs) -> Optional[BaseModel]:
    client = genai.Client(api_key = GEMINI_API_KEY)
    response = client.models.generate_content(
        model = "gemini-2.0-flash",
        contents = prompt if len(args) == 0 and len(kwargs) == 0 else \
                   prompt.format(*args) if len(args) > 0 else prompt.format(**kwargs),
        config = {
            "response_mime_type": "application/json",
            "response_schema": schema,
        },
    )
    try:
        ret = schema.model_validate_json(response.text)
    except Exception as e:
        logging.error(f"Error in GeminiRequestWrapper: {e}")
        os.makedirs("error_response", exist_ok=True)
        with open(f"error_response/{int(time.time())}.json", "w") as f:
            f.write(response.text)
        logging.error(f"Error response saved to error_response/{int(time.time())}.json")
        ret = None
    return ret

def GenerateRelatedQuestionByLLM(query: QuestionSet, num_question_sets: int = 1, num_questions: int = 1) -> Optional[Exam]:
    prompt = f"""
    You are a Chinese middle schoold English exam question generator. 
    Please provide {num_question_sets} question set(s) with {num_questions} question(s) each.

    The student is looking for questions of type {query.type.value} with the similar test points of the following question set:
    {query.model_dump_json(indent=2)}
    """
    return GeminiRequestWrapper(prompt, Exam)