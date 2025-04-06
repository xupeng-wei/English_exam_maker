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
from prompts.prompt_builder import PromptBuilder

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
    prompt_builder = PromptBuilder()
    prompt = prompt_builder.build("related_question_demo", 
                                  num_question_sets=num_question_sets, 
                                  num_questions=num_questions, 
                                  question_type=query.type.value, 
                                  question_set=query.model_dump_json(indent=2))
    return GeminiRequestWrapper(prompt, Exam)