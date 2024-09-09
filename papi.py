from fastapi import FastAPI, HTTPException, Query
from typing import Optional
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import re
import os
import requests
import io

app = FastAPI()

# Regex patterns
phone_number_pattern = r'\b1[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
account_number_pattern = r'\b(?:Account\s*(?:number|Number|No\.|[-\s]*)\s*:?\s*|Acct\s*[-\s]*)\d{1,4}(?:[-\s]?\d{1,4}){0,3}|\b\d{12,16}\b'
address_pattern = r'(?:P\.?O\.? ?Box \d{1,5}[\w\s]*|\d{1,5}[\w\s]+,\s*[A-Z]{2} \d{5}(?:-\d{4})?)|(?:[\d\w\s]+,[\s]*[A-Z]{2}[\s]*\d{5}(?:-\d{4})?)'
bank_names_pattern = r'\b(?:JPMorgan\s+Chase|Chase|Bank\s+of\s+America|BofA|Citibank|Citigroup|Wells\s+Fargo|Goldman\s+Sachs|Morgan\s+Stanley|U\.?S\.?\s+Bank|PNC\s+Financial\s+Services|Truist|Capital\s+One|HSBC|Barclays|American\s+Express)|PNC\s+Bank\b'

def clean_account_number(account_number_str: str) -> str:
    """Clean and return account number digits only."""
    return re.sub(r'\D', '', account_number_str)

def clean_bank_name(bank_name_str: str) -> str:
    """Clean and format bank name."""
    cleaned_name = re.sub(r'[^\w\s]', '', bank_name_str)
    return ' '.join(cleaned_name.split()).title()

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    return text

def download_image(url: str) -> Image.Image:
    """Download and return an image from an external URL."""
    response = requests.get(url)
    response.raise_for_status()
    return Image.open(io.BytesIO(response.content))

def fetch_local_image(image_path: str) -> Image.Image:
    """Fetch and return an image from a local path on the server."""
    if not os.path.isfile(image_path):
        raise HTTPException(status_code=404, detail="Image file not found on server")
    return Image.open(image_path)

@app.post("/extract/")
async def extract_data(
    image_url: Optional[str] = Query(None, description="URL of the image to process"),
    type: str = Query("bankstatement", description="Type of document")
):
    """Extract data from an image URL."""
    if not image_url:
        raise HTTPException(status_code=400, detail="Please provide an image URL.")

    if type.lower() != "bankstatement":
        raise HTTPException(status_code=400, detail="Unsupported document type. Only 'bankstatement' is supported.")

    if image_url.startswith("http://localhost:8000/"):
        local_path = image_url.replace("http://localhost:8000/", "")
        try:
            image = fetch_local_image(local_path)
        except HTTPException as e:
            return {'File Name': local_path, 'Error': str(e)}
    else:
        try:
            image = download_image(image_url)
        except requests.RequestException as e:
            return {'File Name': 'from_url', 'Error': str(e)}

    text = pytesseract.image_to_string(image)
    bank_names = re.findall(bank_names_pattern, text)
    bank_name = clean_bank_name(bank_names[0]) if bank_names else "N/A"
    phone_numbers = re.findall(phone_number_pattern, text)
    account_number_matches = re.findall(account_number_pattern, text)
    account_number = clean_account_number(account_number_matches[0]) if account_number_matches else "N/A"
    addresses = re.findall(address_pattern, text)
    clean_addresses = [' '.join(line.strip() for line in address.split('\n') if line.strip()) for address in addresses]

    result = {
        'File Name': local_path if image_url.startswith("http://localhost:8000/") else 'from_url',
        'Bank Name': bank_name,
        'Bank Address': clean_addresses,
        'Bank Contacts': phone_numbers,
        'Account Number': account_number,
    }

    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
