import random
from typing import Literal, Optional
import sys

sys.path.append("..")
from exam_schema.exam import Exam, QuestionSet, Question, Choices, QuestionType

import logging
logging.basicConfig(
    level=logging.INFO,  # Set logging level (INFO, ERROR, DEBUG, etc.)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Add timestamp
    datefmt="%Y-%m-%d %H:%M:%S",  # Customize timestamp format
    force=True,
)

class OfflineQuestionRetriever:
    def __init__(self, path_to_exam_bank: str):
        self.path_to_exam_bank = path_to_exam_bank
        if not os.path.exists(path_to_exam_bank):
            raise FileNotFoundError(f"Path {path_to_exam_bank} does not exist.")
        self.question_set_index = {}
        for type in QuestionType.__members__.values():
            self.question_set_index[type.value] = {}
            for level in ["grade1", "grade2", "grade3", "others"]:
                self.question_set_index[type.value][level] = []
                
        for type_dir in os.listdir(path_to_exam_bank):
            if os.path.isdir(os.path.join(path_to_exam_bank, type_dir)):
                for level_dir in os.listdir(os.path.join(path_to_exam_bank, type_dir)):
                    if os.path.isdir(os.path.join(path_to_exam_bank, type_dir, level_dir)):
                        for file in os.listdir(os.path.join(path_to_exam_bank, type_dir, level_dir)):
                            if file.endswith(".json"):
                                self.question_set_index[type_dir][level_dir].append(os.path.join(path_to_exam_bank, type_dir, level_dir, file))
                                
    
    def GetQuestionSet(self, type: Optional[QuestionType] = None, 
                       level: Optional[Literal['grade1', 'grade2', 'grade3', 'others']] = None) -> Optional[QuestionSet]:
        if type is None:
            type = random.choice(list(self.question_set_index.keys()))
        else:
            type = type.value
        if level is None:
            value_to_choose = list(self.question_set_index[type].keys())
            value_to_choose.remove("others")
            level = random.choice(value_to_choose)
        question_set_files = self.question_set_index[type][level]
        if len(question_set_files) == 0:
            return None
        question_set_file = random.choice(question_set_files)
        question_set = None
        with open(question_set_file, "r") as f:
            try:
                question_set = QuestionSet.model_validate_json(f.read())
            except Exception as e:
                logging.error(f"Error in GetQuestionSet: {e}")
        return question_set