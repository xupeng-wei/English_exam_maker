from google import genai
from pydantic import BaseModel
import enum
import os

import logging
import time
from tqdm import tqdm

logging.basicConfig(
    filename="/tmp/runtime.log",  # Save logs to a file (optional)
    level=logging.INFO,  # Set logging level (INFO, ERROR, DEBUG, etc.)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Add timestamp
    datefmt="%Y-%m-%d %H:%M:%S",  # Customize timestamp format
    force=True,
)

GEMINI_API_KEY = "" # Your GEMINI API key here

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


prompt = \
"""
You are a Chinese middle school English exam parser. The user provides an English exam collected from the Internew, and requires you to parse them into a structured "exam". Here are requirements of output components:

- A structured "exam" contains "question_sets", which is a list of "question_set".

- A "question_set" has a "type", "context", and "questions" (which is a list of "question").

  - "type" indicates the type of this question set. The "type" has to be one of the following:

    - "Multiple-Choice-Question": the question sets of this type contains a single question. These questions have one or more sentences in text, with <blank>s, and provide 3 or 4 choices for the blank position(s) for students to choose from. The questions are usually used for testing students' understanding to grammars, vocabulary, conversations, etc. 

    - "Reading-Comprehension-With-Multiple-Choices": the question sets of this type provide a passage as "context", and goes with several multiple-choice questions related to the passage. The questions usually check students' reading comprehension capability. 

    - "Reading-Comprehension-With-True-or-False": the question sets of this type provide a passage as "context", and goes with several statements related to the content of the passage. Students will need to choose "T" (True) or "F" (False) based on whether the statement consistent with the passage. 

    - "Cloze-With-Multiple-Choices": the question sets of this type provide a passage as "context", with <blank>s. Each <blank> corresponds to a question in "questions". These questions do not have extra "text", but with 3 or 4 choices that could be filled in the <blank>.

    - "Cloze-With-Free-Responses": the question sets of this type provide a passage as "context", with <blank>s. Each <blank> corresponds to a question in "questions". These questions do not provide extra 'text" or "choices", and students are expected to fill a word in the <blank>.

  - "context" provides the additional materials required for solving certain types of question sets. If the type is "Multiple-Choice-Question", it does not require any context, so you may leave the context as an empty string.

- A "question" consist of "text", "choices", "answer", "is_answer_provided", "explanation", "test_point": 

  - "text": the text of a certain question. The questions in "Multiple-Choice-Question", "Reading-Comprehension-With-Multiple-Choices", "Reading-Comprehension-With-True-or-False" will have "text" field, which contains the text of the question (if there are multiple lines, like a conversation, you should include the multiple lines), but not including the choices, while the questions in "Cloze-With-Multiple-Choices" and "Cloze-With-Free-Responses" question sets don't require any "text", so you may leave the context as an empty string.

  - "choices": the three or four choices of a multiple choice questions, with "A", "B" and "C" fields if there are three choices, or "A", "B", "C", and "D" fields if there are four choices. The questions in "Multiple-Choice-Question", "Reading-Comprehension-With-Multiple-Choices", "Cloze-With-Multiple-Choices" question sets have "choices" field, while "Reading-Comprehension-With-True-or-False" and "Cloze-With-Free-Responses" do not require choices, so you may leave all the fields in "choices" as empty strings. 

  - "answer": the answer to the question. The answers to a multiple choice questions (including questions in the "Multiple-Choice-Question", "Reading-Comprehension-With-Multiple-Choices", "Cloze-With-Multiple-Choices" question sets) must be "A", "B", "C", or "D". The answers to a question in "Reading-Comprehension-With-True-or-False" question sets must be "T" or "F". No constraint on the answers to "Cloze-With-Free-Responses". 

  - "is_answer_provided": if the answer can be found in the provided document (as "答案", "参考答案", or so), this field should be true. Otherwise, you try to come up with the answer in the "answer" field, and fill in this field with false.

  - "explanation": provide the reason why we should use this answer. No more than 50 words.

  - "test_point": use up to 6 keywords to summarize the test point of the question. For example, "Verb Tenses; Subject-Verb Agreement; Passive Voice". Possible keywords can be any of, but not limited to, the following: Prepositions, Verb Tenses, Subject-Verb Agreement, Word Formation, Collocations, Synonyms & Antonyms, Pronouns, Passive Voice, Conditional Sentences, Reading Comprehension, Cloze Test, Fixed Expressions, Phrasal Verbs, Modal Verbs, Articles, Comparatives & Superlatives, Conjunctions, Reported Speech, Question Formation, Gerunds & Infinitives, Relative Clauses, Sentence Structure, Idioms & Phrases, Word Order, Countable & Uncountable Nouns, Determiners, Logical Connectors, Double Negatives, Parallel Structure, Contextual Vocabulary, Inference Skills, Main Idea Identification, Author’s Purpose, Tone & Attitude, Fact vs. Opinion, Reference Words, Cause & Effect, Synonym Replacement, Antonym Clues, Skimming & Scanning, Implicit Information, Logical Progression, Pronoun Reference, Text Organization, Supporting Details, Summarization, Transition Words, Time Expressions, Sentence Completion, Fixed Sentence Patterns, Redundancy Avoidance, Cohesion & Coherence, Style & Register, Genre Recognition, Figurative Language, Commonly Confused Words, Sentence Transformation.

Here are some additional rules:

- Do not include Listening tests into your response. Similarly, skip the questions which do not belong to any of the types listed above.

- The parsed "text" or "context" should not contain any underscores. All the blanks should be represented as <blank>, or <blank text=(some text, e.g., the question number)>.

- If you use <blank>, you should not let the <blank> swallow the space before and after it.

- Not all the content provided belongs to a question set.

- No need to include the question number and parenthesis in the front.

- "\n" in the content might be a space or a new line. Shouldn't include "\n" in your output.

- If the original text has typos, spelling issues, or format issues, correct them.

---

Here is the input:

"""


paths = [
    ("~/crawling/trjlseng_parsed/cyst", "~/crawling/parsed_exams/trjlseng/cyst"),
    ("~/crawling/trjlseng_parsed/cest", "~/crawling/parsed_exams/trjlseng/cest"),
    ("~/crawling/trjlseng_parsed/csst", "~/crawling/parsed_exams/trjlseng/csst"),
    ("~/crawling/zww.cn_nianji1", "~/crawling/parsed_exams/zww.cn/nianji1"),
    ("~/crawling/zww.cn_nianji2", "~/crawling/parsed_exams/zww.cn/nianji2"),
    ("~/crawling/zww.cn_nianji3", "~/crawling/parsed_exams/zww.cn/nianji3"),
    ("~/crawling/zww.cn_zhongkao", "~/crawling/parsed_exams/zww.cn/zhongkao"),
]

arg_list = []
for (in_path, out_path) in paths:
    for file in os.listdir(in_path):
        if file.endswith(".json"):
            arg_list.append((in_path, file, out_path))
    if not os.path.exists(out_path):
        os.makedirs(out_path)

failed_list = []

def InternalParseExams(in_path, exam_name, out_dir):
    exam_path = os.path.join(in_path, exam_name)
    if not os.path.exists(exam_path) or not exam_path.endswith(".json"):
        raise Exception("Input error: [{}, {}]".format(in_path, exam_name))
    
    with open(exam_path, "r") as f:
        exam = f.read()
    
    try:
        client = genai.Client(api_key = GEMINI_API_KEY)
        response = client.models.generate_content(
            model = "gemini-2.0-flash",
            contents = prompt + exam,
            config = {
                "response_mime_type": "application/json",
                "response_schema": Exam,
            },
        )
    except:
        raise Exception("Failed to obtain response: [{}, {}]".format(in_path, exam_name))
    
    out_exam = os.path.join(out_dir, exam_name)
    try:
        with open(out_exam, "w") as f:
            f.write(response.text)
    except:
        raise Exception("Failed to write: [{}]".format(out_exam))

    try:
        exam_obj = Exam.model_validate_json(response.text)
    except:
        raise Exception("Failed to validate the output: raw output was saved to [{}]".format(out_exam))
    
    try:
        with open(out_exam, "w") as f:
            f.write(exam_obj.model_dump_json(indent=4))
    except:
        raise Exception("Failed to write json to: [{}]".format(out_exam))

    return response

def ParseExams(in_path, exam_name, out_dir):
    ret = None
    try:
        time.sleep(2)
        start = time.perf_counter()
        ret = InternalParseExams(in_path, exam_name, out_dir)
        end = time.perf_counter()
        logging.info("Spent [{:.6f}] seconds. Parsed [{}/{}]. Saved to [{}]".format(end - start, in_path, exam_name, out_dir))
    except Exception as e:
        failed_list.append((in_path, exam_name, out_dir))
        logging.error(f" Exception: {e}")
    return ret

if __name__ == "__main__":
    failed_list_path = "~/crawling/parsed_exams/failed_list.txt"
    with open(failed_list_path, "w") as f:
        pass

    logging.warning("========Start Parsing exercises========")
    start = time.perf_counter()
    for arg in tqdm(arg_list):
        in_path, exam_name, out_dir = arg
        if os.path.exists(os.path.join(out_dir, exam_name)):
            continue
        ret = ParseExams(*arg)
        if ret is None:
            with open(failed_list_path, "a") as f:
                f.write('("{}", "{}", "{}")\n'.format(arg[0], arg[1], arg[2]))
    end = time.perf_counter()
    logging.warning(f"===Summary: spent [{end - start}] seconds, #works [{len(arg_list)}], #failures [{len(failed_list)}]")
    logging.warning("========End=======")