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
