# English Exam Question Maker 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![WIP](https://img.shields.io/badge/status-active%20development-orange)](https://github.com/your-repo)

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

