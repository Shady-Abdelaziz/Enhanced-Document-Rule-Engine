import json
import re
import subprocess
from datetime import datetime
from dateutil import parser
import pytesseract
import pdfplumber
from PIL import Image
from io import BytesIO

FIELD_CATEGORIES = {
    "money": ["total_amount", "payment_amount", "subtotal", "tax_amount"],
    "date": ["invoice_date", "due_date", "payment_date"],
    "time": ["issue_time", "processing_time"],
    "text": ["invoice_number", "customer", "vendor"]
}

FIELD_DISPLAY_NAMES = {
    "total_amount": "Total Amount",
    "payment_amount": "Payment Amount",
    "subtotal": "Subtotal",
    "tax_amount": "Tax Amount",
    "invoice_date": "Invoice Date",
    "due_date": "Due Date",
    "payment_date": "Payment Date",
    "issue_time": "Issue Time",
    "processing_time": "Processing Time",
    "invoice_number": "Invoice Number",
    "customer": "Customer",
    "vendor": "Vendor"
}

def extract_text_from_document(uploaded_file, file_bytes):
    if uploaded_file.type == "application/pdf":
        try:
            text = []
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                for page in pdf.pages[:10]:  
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text.strip())
            return "\n\n".join(text)
        except Exception as e:
            raise Exception(f"PDF Error: {str(e)}")
    else:
        try:
            image = Image.open(BytesIO(file_bytes))
            return pytesseract.image_to_string(image)
        except Exception as e:
            raise Exception(f"Image Error: {str(e)}")

def run_ollama_command(prompt, model="llama3:8b"):
    try:
        process = subprocess.Popen(
            ["ollama", "run", model, prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        stdout, _ = process.communicate()
        return stdout.strip()
    except Exception as e:
        raise Exception(f"Ollama error: {str(e)}")

def extract_json_from_response(response):
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        return json.loads(response[start:end])
    except:
        return {}
def parse_rule(rule_text):

    rule_prompt = f"""
    unerstand and Convert this rule to JSON with EXACTLY these fields: category, condition, value.
    Follow these specifications precisely:

    CATEGORIES (use exactly one):
    - "money" (for amounts)
    - "date" (format: YYYY-MM-DD)
    - "time" (format: HH:MM:SS)

    CONDITIONS (use exactly one):
    - "equals", "not_equals"
    - "greater_than", "less_than" (for money)
    - "before_date", "after_date" (for dates)
    - "contains", "not_contains" (for text)

    OUTPUT EXAMPLES:
    {{
        "category": "money",
        "condition": "greater_than",
        "value": 1000
    }}
    {{
        "category": "date",
        "condition": "before_date",
        "value": "2025-01-01"
    }}

    STRICT REQUIREMENTS:
    1. Money values must be numbers (no symbols)
    2. Dates must be YYYY-MM-DD format
    3. Times must be HH:MM:SS format
    4. Return ONLY the JSON object with NO other text

    Rule to convert: "{rule_text}"
    """

    try:
        response = run_ollama_command(rule_prompt)
        return extract_json_from_response(response)
    except Exception as e:
        st.error(f"Rule parsing error: {str(e)}")
        return None
    
    
def extract_data_from_text(document_text):
    max_chars = 5000
    truncated_text = document_text[:max_chars]
        
    data_prompt = f"""
    Extract structured data from this document and return ONLY a JSON object. Follow these rules exactly:

    OUTPUT FORMAT:
    {{
    "money": "extracted money value",
    "date": "extracted date value",
    "time": "extracted time value",
    }}


    STRICT RULES:
    1. Remove ALL currency symbols ($, €, £ etc.)
    2. Convert dates to EXACTLY YYYY-MM-DD format
    3. Convert times to EXACTLY HH:MM:SS format
    4. Include only the first detected value in each category
    5. Return ONLY the JSON object with NO other text


    Document Text:
    {truncated_text}
    """
    try:
        response = run_ollama_command(data_prompt)
        return extract_json_from_response(response)
    except Exception as e:
        st.error(f"Data extraction error: {str(e)}")
        return {}
    

def validate_rule(rule, data):
    if not rule or not data:
        return {
            "rule": rule,
            "status": "Error",
            "message": "Missing rule or data",
            "expected_value": rule.get("value") if rule else None,
            "actual_value": None
        }

    category = rule.get("category")
    condition = rule.get("condition")
    expected = rule.get("value")
    actual = data.get(category)

    if actual is None:
        return {
            "rule": rule,
            "status": "Error",
            "message": f"No {category} in document",
            "expected_value": expected,
            "actual_value": None
        }

    try:
        if category == "money":
            result = _compare_numbers(condition, float(actual), float(expected))
        elif category in ["date", "time"]:
            result = _compare_dates(condition, actual, expected)
        else:
            result = _compare_text(condition, str(actual), str(expected))

        return {
            "rule": rule,
            "status": "PASS" if result else "FAIL",
            "expected_value": expected,
            "actual_value": actual
        }
    except Exception as e:
        return {
            "rule": rule,
            "status": "Error",
            "message": str(e),
            "expected_value": expected,
            "actual_value": actual
        }

def _compare_numbers(condition, actual, expected):
    if condition == "equals": return actual == expected
    if condition == "not_equals": return actual != expected
    if condition == "greater_than": return actual > expected
    if condition == "less_than": return actual < expected
    return False

def _compare_dates(condition, actual, expected):
    try:
        a = parser.parse(actual)
        e = parser.parse(expected)
        
        if condition == "equals": return a == e
        if condition == "not_equals": return a != e
        if condition == "before_date": return a < e
        if condition == "after_date": return a > e
        
        return False
    except Exception as e:
        print(f"Date comparison error: {str(e)}")
        return False
    
    
def _compare_text(condition, actual, expected):
    actual = actual.lower()
    expected = expected.lower()
    if condition == "equals": return actual == expected
    if condition == "not_equals": return actual != expected
    if condition == "contains": return expected in actual
    if condition == "not_contains": return expected not in actual
    return False