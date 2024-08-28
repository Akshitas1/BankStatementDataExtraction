import os
import re
import pytesseract
from PIL import Image
import json

# Directory containing images
image_folder = 'data'

# Regex patterns
phone_number_pattern = r'\b1[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
account_number_pattern = r'\b(?:Account\s*(?:number|Number|No\.|[-\s]*)\s*:?\s*|Acct\s*[-\s]*)\d{1,4}(?:[-\s]?\d{1,4}){0,3}|\b\d{12,16}\b'
address_pattern = r'(?:P\.?O\.? ?Box \d{1,5}[\w\s]*|\d{1,5}[\w\s]+,\s*[A-Z]{2} \d{5}(?:-\d{4})?)|(?:[\d\w\s]+,[\s]*[A-Z]{2}[\s]*\d{5}(?:-\d{4})?)'
bank_names_pattern = r'\b(?:JPMorgan\s+Chase|Chase|Bank\s+of\s+America|BofA|Citibank|Citigroup|Wells\s+Fargo|Goldman\s+Sachs|Morgan\s+Stanley|U\.?S\.?\s+Bank|PNC\s+Financial\s+Services|Truist|Capital\s+One|HSBC|Barclays|American\s+Express)|PNC\s+Bank\b'

# Initialize list to store results
results = []

# Function to clean account numbers
def clean_account_number(account_number_str):
    digits = re.sub(r'\D', '', account_number_str)
    return digits

# Function to clean bank names
def clean_bank_name(bank_name_str):
    # Remove special characters and extra spaces
    cleaned_name = re.sub(r'[^\w\s]', '', bank_name_str)
    cleaned_name = ' '.join(cleaned_name.split())
    
    # Capitalize each word
    cleaned_name = cleaned_name.title()
    
    # Common fixes for known issues
    replacements = {
        'Chases': 'Chase',
        'Uppank': 'Upbank', 
        'Pnc Access Checking Statement Pnc Bank': 'PNC Bank',  
        'Wells Fargo Simple Business Checking': 'Wells Fargo'
    }
    
    # Apply replacements
    for old, new in replacements.items():
        if old in cleaned_name:
            cleaned_name = cleaned_name.replace(old, new)
    
    return cleaned_name

# Process each image in the folder
for filename in os.listdir(image_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        # Load image
        image_path = os.path.join(image_folder, filename)
        image = Image.open(image_path)
        
        # Extract text from image
        text = pytesseract.image_to_string(image)
        
        # Extract bank name
        bank_names = re.findall(bank_names_pattern, text)
        bank_name = clean_bank_name(bank_names[0]) if bank_names else "N/A"

        # Extract phone numbers
        phone_numbers = re.findall(phone_number_pattern, text)
        
        # Extract account numbers
        account_number_matches = re.findall(account_number_pattern, text)
        account_number = clean_account_number(account_number_matches[0]) if account_number_matches else "N/A"
        
        # Extract addresses using regex
        addresses = re.findall(address_pattern, text)
        clean_addresses = [' '.join(line.strip() for line in address.split('\n') if line.strip()) for address in addresses]
        
        # Store results
        results.append({
            'File Name': filename,
            'Bank Name': bank_name,
            'Bank Address': clean_addresses,
            'Bank Contacts': phone_numbers,
            'Account Number': account_number,
        })

# Convert results to JSON format
json_results = json.dumps(results, indent=4)

# Save results to JSON file
with open('extracted_data.json', 'w') as json_file:
    json_file.write(json_results)

print("Data extraction completed and saved to extracted_data.json")
