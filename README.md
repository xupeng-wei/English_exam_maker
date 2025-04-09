# English Exam Question Maker 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![WIP](https://img.shields.io/badge/status-active%20development-orange)](https://github.com/xupeng-wei/English_exam_maker)
[![Hugging Face Datasets](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-blue)](https://huggingface.co/datasets/dry-melon/Chinese-middle-school-English-exam-questions)

An intelligent system for automatically generating and customizing English exam questions for Chinese middle school students.

## ✨ Core Features

- **Hybrid Question Sources**
  - Offline question bank: Pre-collected exam questions from public websites
  - LLM generation: Dynamically create new questions using language models
- **Flexible Generation**
  - Generate similar questions based on existing test points
  - Support multiple question types and grade levels (Grades 7-9)
- **Scalable System**
  - Combine rule-based processing with LLM capabilities
  - Unlimited question generation beyond offline database limits

## 💡 System Overview

### Data Pipeline
1. **Data Collection**: Crawl raw exam questions from public educational websites
2. **Data Processing**:

Two approaches for converting unstructured raw data to structured format:

   - Rule-based processing: Format standardization using regex patterns
   - LLM-based processing: Structure parsing, semantic analysis for knowledge point identification, context-aware content generation

Both pipelines output structured JSON data that gets stored in the unified question bank.

3. **Question Generation**:
   - Retrieve from processed database
   - Generate new questions using LLMs

### Key Advantages
- **Dual-source questions**: Combine verified existing questions with AI-generated content
- **Infinite scalability**: Overcome offline database limitations through LLM generation
- **Customization**: Control question types and difficulty levels

## 📊 Data

### Quick Start

To access the dataset, use the following scripts:

```python
from datasets import load_dataset

# Load all data
dataset = load_dataset("dry-melon/Chinese-middle-school-English-exam-questions", name="default")
```

Split by grade:
```python
dataset = load_dataset("dry-melon/Chinese-middle-school-English-exam-questions", name="grade")
```

Split by question type:
```python
dataset = load_dataset("dry-melon/Chinese-middle-school-English-exam-questions", name="question_type")
```

### Data Source

http://shijuan.zww.cn 

- Contains middle school English exam questions (Grades 7-9) and Chinese high school entrance exam materials  
- Data characteristics:  
  - Unstructured text format  
  - No categorization by question types or test points  
  - Partial questions lack answers/explanations  

https://www.trjlseng.com

- Collects exam papers from multiple grades and schools  
- Data characteristics:  
  - PDF/doc/docx file formats  
  - Unstructured text content  

### Data Processing

#### Data Summary

- 35,211 question sets in total.
- By grade:
  - Grade 7: 10,692
  - Grade 8: 9,795
  - Grade 9: 14,724
- By question type:
  - Multiple-Choice-Question: 30,478
  - Reading-Comprehension-With-Multiple-Choices: 2,734
  - Reading-Comprehension-With-True-or-False: 561
  - Cloze-With-Multiple-Choices: 1,216
  - Cloze-With-Free-Responses: 222

#### Data Collection
See sample code in `crawl` folder:

1. **Blog Data Crawling**  
   - Uses Python `requests` library for content retrieval  
   - Extracts exam content from HTML using `beautifulsoup`  
   - Reference: `crawl/crawl_instance_0.ipynb`

2. **Document Processing**  
   - Downloads PDF/doc files via `requests`  
   - Converts files to text:  
     - PDF parsing with `fitz` (PyMuPDF) 
     - DOC/DOCX parsing with `docx` library  
   - Outputs JSON format data  
   - Reference: `crawl/crawl_instance_1.ipynb`, `crawl/instance_1_convert_to_json.ipynb`

Upon this step, 4,481 blogs and exam papers are collected:

- From zww.cn: 1190 blog articles for Grade 7, 1191 for Grade 8, 1213 for Grade 9, and 813 for high school entrance exams
- From trjlseng.com: 26 exam papers for Grade 7, 24  for Grade 8, and 24 for Grade 9

All the data up to this point are highly unstructured:

- They have different format: some of them are blog articles, and some are pdf / doc
- They have different structures: 
  - Some use underscores (__) to represent blanks, and some use parentheses
  - Some of them have answers and explanations right after the question, while some leave the answer to the end of the articles. Some data do not have answers with questions.
  - ...
- Some data contain materials irrelavent to our crawling target:
  - The main targeting question types include multiple choice questions, reading comprehension with multiple choices / True-or-False, cloze with multiple choices / free responses. However, raw materials may include questions of other types, such as listening comprehension, writing, and other novel types of questions that are rarely used in formal exams. Some articles mainly introduce strategies of solving problems and only with few examples.  

#### Data Processing

##### Objective Data Schema

The objective of data processing is to extract all the questions of our interest types from raw materials, and parse them into a structured format, defined in `exam_schema/exam.py`.

An atomic unit of question in this repo is defined as a "QuestionSet", which consists of:

- type: enum, indicating the question type, including "Multiple-Choice-Question", "Reading-Comprehension-With-Multiple-Choices", "Reading-Comprehension-With-True-or-False", "Cloze-With-Multiple-Choices", "Cloze-With-Free-Responses"
- context: string, containing the necessary context for a question set. "Multiple-Choice-Question" does not need context so this field is empty. For reading comprehension, context should be reading materials. For cloze questions, context should be passages with blanks.
- questions: a list of question. "Multiple-Choice-Question" is defined as a singleton, i.e., each mcq contain only one question. Other types of questions are actually "not a question", but a set of questions with a common context. This motivates the definition of QuestionSet.

A question consists of the following components:

- text: string, the instruction of a question. For "Multiple-Choice-Question", the text is usually few sentences or a conversation with one or two blanks. For "Reading-Comprehension-With-Multiple-Choices", the text is a question related to the reading material. For "Reading-Comprehension-With-True-or-False", the text is a statement related to the reading material. Cloze questions do not have text, as they don't need specific instructions for each single question
- choices: consists of four string fields named after "A", "B", "C", "D", indicating choices of an MCQ. "Reading-Comprehension-With-True-or-False" and "Cloze-With-Free-Response" do not require texts in choices.
- answer: string, the answer to the question
- is_answer_provided: bool, "true" means the answer can be found in the raw material, while "false" means the answer was filled in during data processing
- explanation: string, the few-sentence reasoning steps of the answer
- test_point: string, a few short phrases that explain the tested knowledge domain of the question

#####  Convert the unstructured data to structured ones

Both rule-based methods and LLM-based methods were used to extract questions of interest from raw materials

- Rule-based method: only for multiple choice questions

  - `rule_based_preprocess/mcq_regex_extractor.ipynb`

  - Pre-process the raw materials: convert special characters to normal letters and characters. 

  - Use RegEx to extract MCQs and extract choices: 

    - Use the signal words to detect the start of ther MCQ section (e.g., 选择填空)
    - List possible choice patterns to match the MCQ choices, and separate questions accordingly

  - Issues:

    - Rules are usually complicated and hard to tune
    - Difficult to compose rules that covers all the possible corner cases

    That's why we switched to LLM-based method

- LLM-based processing: 

  - `lm_based_preprocess/run_llm_parse_exercises.py`
  - Use gemini flash 2.0 API. 
  - Compose a system prompt with explanations of the expected data structures and additional rules
  - Pass the pydantic data model as the input in order to obtain structured output
  - Pros:
    - This method works for all the question types of our interest
    - LLM can fill in the answer and explanation fields even if they are not provided in raw materials
  - Issues:
    - Sometimes it can mistakenly parse other miscellaneous types into types of interest

Upon this step, there are 52,581 question sets.

By question type:

- Multiple-Choice-Question: 41,269 question sets (if multiple questions in one question set produced by LLM, count each of them as singleton, as MCQ question sets should be a singleton)
- Reading-Comprehension-With-Multiple-Choices: 3,824 question sets
- Reading-Comprehension-With-True-or-False: 755 question sets
- Cloze-With-Multiple-Choices: 1,939
- Cloze-With-Free-Responses: 4,794

By grade: 

- Grade 7: 17,138 question sets
- Grade 8: 14,728 question sets
- Grade 9:  20,715 question sets

#####  Post-processing: filter the invalid data

What constitutes invalid data?

- Incomplete question sets: e.g., MCQ without any string in choices, reading comprehension with incomplete passages
- Mismatched type: such as translation questions being parsed as cloze with free response
- Duplicated questions: question sets with essentially the same content
- ...

Method: rule-based post-processing

- `rule_based_preprocess/preprocess_exercises.ipynb`
- Common:
  - Normalization: convert the double byte non-Chinese characters (e.g., parenthesis （）) to single byte. 
  - Deduplication: use exact match strategy. For given text, we first normalize the text by converting all letters to lowercase, remove all the non-English characters, and use nltk to tokenize the text. Then, calculate the md5 of the string produced by the concatenation of tokens. 
  - Check if the given text has more than n_max consecutive Chinese characters: typically formal exam questions of Chinese middle school English exam won't contain many Chinese characters. The Chinese used in the exam questions are usually used for providing necessary translation for advanced English words for middle school students, or for question instructions. In processed data the instruction for each question type won't be needed, and the translation for single word won't be long, so substrings with long consecutive Chinese characters are very unlikely to appear in the final results. We use it as a criterion to filter data. 
- Multiple-Choice-Question:
  - Choice validation: check if a question is a MCQ. Questions with empty choices A, B, or C, cannot be MCQ. 
  - Text validation: MCQ should have a non-empty text field. 
  - Question splitting: as per the data model, a MCQ question set consists of single questions, so if a raw question set contains multiple questions, separate them into singleton question sets.
  - Parse blank: normalize the blanks in the text to the standard format \<blank\> or \<blank text=...\>, as many as possible
  - Deduplication: concantenate question text and options, and then run the common deduplication tool. 
- Reading-Comprehension:
  - Context validation: generally, reading passages should be longer than few round conversations or one short paragraph. To filter the materials potentially coming from other rare question types (e.g., answering questions based on table information, graph information, which only contains few words), set a threshold for the length of context (<50 normalized tokens), and filter question sets with context shorter than the threshold. 
  - Choice validation: for Reading-Comprehension-With-Multiple-Choice, run the same choice validation as MCQ. For Reading-Comprehension-With-True-or-False, all choices should be empty.
  - Text validation: Reading-Comprehension-With-Multiple-Choice has non-empty text fields, while True-or-False has empty text fields.
  - Deduplication: concantenate context and question text, and then run the common deduplication tool.
- Cloze:
  - Context validation: should satisfy the requirement mentioned in Reading-Comprehension. Besides, cloze passages must have blanks. 
  - Text validation: all cloze questions should not have text.
  - Blank regularization: the format \<blank text=(blank_number)\> or simply \<blank\> is desirable, as it is good for deduplication, and convenient for the downstream use. Currently we converted the following patterns:
    - underscores: _, ___, ____
    - blanks with numbers in wrong locations: e.g., \<blank\>9\<blank\>, \<blank\>(8), (8)\<blank\>, ...
    - unrecognized text in blank structure: e.g., \<blank text=non-number text...\>
  - For free-response: need to filter simple cloze questions for single sentences. The language model will parse these questions as Cloze-With-Free-Response, but they are not of the type of our interests. Usually the context of these mistakenly parsed problems contains multiple questions, each with a number in the front of each line, so we first detect if there are more than three starting question number patterns, and then filter the question sets of this type. 
  
  See the number of remaining question sets in [Data Summary](#data-summary) subsection. The overall filter rate is 33.0% Here list the filter rate of each question type:
  
  - Multiple-Choice-Question: 26.1%
  - Reading-Comprehension-With-Multiple-Choices: 28.5%
  - Reading-Comprehension-With-True-or-False: 25.7%
  - Cloze-With-Multiple-Choices: 37.3%
  - Cloze-With-Free-Responses: 95.4% 
    (as the given prompt asks the model to catch questions with blanks that allow free responses, while some common questions of other type, such as writing or grammar questions with free responses also satisfy the given conditions. Most of these cases can be filtered by rules)

## ⚙️ [WIP] Question Maker

### Offline Question Selector

`question_maker/offline.py`: randomly pick one or more question sets upon user's requests

### Similar Question Maker

#### PromptBuilder

All the prompt templates are stored in `prompts` folder with suffix `.yaml`. Each prompt template files can contains multiple templates. Each template contains a `template` field and a `variable` field. In a template, users can define other fields and cite as variables in `template`. For example:

```yaml
a_demo_template:
  variables: ["system", "exam"]
  template: |
    {{ system }}
    
    Now provide me with a question set similar to the following:
    {{ exam }}
  system: |
    You are an exam maker bot.
```

Currently `template` does not support nested variables. 

The prompt templates can be parsed by `PromptBuilder` implemented in `prompts/prompt_builder.py`, using jinja2 to build actual prompts.

#### Prototype

`question_maker/gemini.py` is a prototype version of question maker, using gemini flash 2.0 API. Currently this part works pretty well for Multiple-Choice-Questions. Still working on other types of questions, and extracting prompt templates. 