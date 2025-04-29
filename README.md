# Advanced Document Validator Pro

Advanced Document Validator Pro is a Streamlit web application that leverages an LLM backend to extract structured data from documents (PDFs or images) and validate that data against user-defined rules.

## Features
- **Document Processing**: Upload PDF or image files, extract text with `pdfplumber` (for PDFs) or `pytesseract` (for images), and preview or edit the raw text.
- **Data Extraction**: Use an LLM (via the Ollama CLI) to parse extracted text into structured JSON fields (`money`, `date`, `time`, `text`).
- **Rule Management**: Define validation rules in natural language (e.g. “Invoice date must be after 2025-01-01”), automatically parsed into JSON (`category`, `condition`, `value`).
- **Validation Dashboard**: Run all rules against the extracted data, view a summary of passes/fails, and inspect detailed results with rich styling.
- **Interactive UI**: Custom CSS for clear rule cards, progress indicators, expandable details, and session-state persistence.

## Project Structure
- **app.py**  
  Streamlit application entry point; handles UI layout, session state, file uploads, editing, and rule/value interactions  
- **llm.py**  
  Core logic for text extraction, LLM prompting (via `ollama run`), JSON parsing, and rule validation  
- **requirements.txt**  
  Lists all Python dependencies  
- **README.md**  
  This documentation

## Installation
1. Clone the repository to your local machine  
2. Create and activate a Python virtual environment  
3. Install dependencies with `pip install -r requirements.txt`

## Usage
1. Launch the app by running `streamlit run app.py`  
2. In your web browser, use the sidebar to navigate between:  
   - 📄 **Document Processing**: Upload and extract data  
   - ⚙️ **Rule Management**: Add, edit, or delete validation rules  
   - ✅ **Validation Dashboard**: Execute validations and review results  

## Configuration
- Ensure the Ollama CLI is installed and configured for your chosen LLM model (default `llama3:8b`)  
- Tesseract OCR must be installed on your system and available in your `PATH`

## Contributing
Contributions are welcome! To propose improvements or report issues:  
1. Fork the repository  
2. Create a new feature branch  
3. Submit a pull request with a clear description of your changes

## License
This project is released under the MIT License. Feel free to use, modify, and distribute.
