# 📄 Advanced Document Validator Pro

Advanced Document Validator Pro is a user-friendly web application built with Streamlit that extracts structured data from documents (PDFs or images) and validates it against user-defined rules, powered by a local language model.

## 🔧 Features

- **Flexible Document Uploads**  
    Upload PDFs or images for automatic text extraction using `pdfplumber` or `pytesseract`.  
- **Intelligent Data Extraction**  
    Structured fields like date, amount, time, and text are parsed from raw text using an LLM backend (via Ollama CLI).  
- **Custom Rule Engine**  
    Define validation rules in plain language (e.g. “Amount must be greater than 1000”) and let the app interpret and apply them.  
- **Validation Summary Dashboard**  
    View which rules pass or fail, with expandable insights and styled result cards.  
- **Interactive UI**  
    Clean, intuitive interface with support for in-session editing, rule management, and dynamic state handling.  

## 📁 Project Structure

    project-root/
    ├── app.py           Main Streamlit application  
    ├── llm.py           Text extraction, LLM interfacing, validation logic  
    ├── requirements.txt Python dependencies  
    └── README.md        Project documentation  

## 🚀 Getting Started

### Installation

1. Clone the repository  
2. Create and activate a virtual environment  
3. Install dependencies:  
    pip install -r requirements.txt

### Launch the App

    streamlit run app.py

### Navigate the UI

- 📄 **Document Processing** – Upload files and extract text  
- ⚙️ **Rule Management** – Define or edit validation rules  
- ✅ **Validation Dashboard** – Run and review validations  

## ⚙️ Requirements

- Ollama installed and running with your preferred local LLM model (default: `llama3:8b`)  
- Tesseract OCR installed and available in your system `PATH`  

## 🤝 Contributing

We welcome community contributions!  
To contribute:  
1. Fork the repository  
2. Create a feature branch  
3. Submit a pull request with a clear explanation of your changes  

## 📄 License

This project is licensed under the MIT License. You’re free to use, modify, and share it.
