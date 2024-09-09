from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import re
import os
import json

app = FastAPI()

# Regex patterns
phone_number_pattern = r'\b1[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
account_number_pattern = r'\b(?:Account\s*(?:number|Number|No\.|[-\s]*)\s*:?\s*|Acct\s*[-\s]*)\d{1,4}(?:[-\s]?\d{1,4}){0,3}|\b\d{12,16}\b'
address_pattern = r'(?:P\.?O\.? ?Box \d{1,5}[\w\s]*|\d{1,5}[\w\s]+,\s*[A-Z]{2} \d{5}(?:-\d{4})?)|(?:[\d\w\s]+,[\s]*[A-Z]{2}[\s]*\d{5}(?:-\d{4})?)'
bank_names_pattern = r'\b(?:JPMorgan\s+Chase|Chase|Bank\s+of\s+America|BofA|Citibank|Citigroup|Wells\s+Fargo|Goldman\s+Sachs|Morgan\s+Stanley|U\.?S\.?\s+Bank|PNC\s+Financial\s+Services|Truist|Capital\s+One|HSBC|Barclays|American\s+Express)|PNC\s+Bank\b'

# Function to clean account numbers
def clean_account_number(account_number_str):
    digits = re.sub(r'\D', '', account_number_str)
    return digits

# Function to clean bank names
def clean_bank_name(bank_name_str):
    cleaned_name = re.sub(r'[^\w\s]', '', bank_name_str)
    cleaned_name = ' '.join(cleaned_name.split())
    cleaned_name = cleaned_name.title()
    return cleaned_name

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

@app.post("/extract/")
async def extract_data(folder_name: str = Query('data', description="Folder name to extract data from")):
    results = []

    # Check if the provided folder exists
    if not os.path.exists(folder_name):
        raise HTTPException(status_code=404, detail="Data folder not found")
    
    # Process each file in the folder
    for filename in os.listdir(folder_name):
        file_path = os.path.join(folder_name, filename)
        file_ext = filename.split('.')[-1].lower()
        
        # Check if it's a file (not a directory)
        if not os.path.isfile(file_path):
            continue
        
        try:
            if file_ext in ['png', 'jpg', 'jpeg']:
                # Process image file
                image = Image.open(file_path)
                text = pytesseract.image_to_string(image)
            elif file_ext == 'pdf':
                # Process PDF file
                text = extract_text_from_pdf(file_path)
            else:
                continue
            
            # Extract data
            bank_names = re.findall(bank_names_pattern, text)
            bank_name = clean_bank_name(bank_names[0]) if bank_names else "N/A"
            phone_numbers = re.findall(phone_number_pattern, text)
            account_number_matches = re.findall(account_number_pattern, text)
            account_number = clean_account_number(account_number_matches[0]) if account_number_matches else "N/A"
            addresses = re.findall(address_pattern, text)
            clean_addresses = [' '.join(line.strip() for line in address.split('\n') if line.strip()) for address in addresses]
            
            result = {
                'File Name': filename,
                'Bank Name': bank_name,
                'Bank Address': clean_addresses,
                'Bank Contacts': phone_numbers,
                'Account Number': account_number,
            }
            
            results.append(result)
        
        except Exception as e:
            results.append({'File Name': filename, 'Error': str(e)})
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,  host="0.0.0.0", port=8000)

