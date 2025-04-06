from google import genai
from pydantic import BaseModel
import enum
import os

import logging
import time
from tqdm import tqdm

import sys
sys.path.append("..")
from exam_schema.exam import Exam, QuestionSet, Question, Choices, QuestionType

logging.basicConfig(
    filename="/tmp/runtime.log",  # Save logs to a file (optional)
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

from prompts.prompt_builder import PromptBuilder
prompt_builder = PromptBuilder()

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
            contents = prompt_builder.build("exam_parser", exam=exam),
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