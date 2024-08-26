import os
import re
import pytesseract
from PIL import Image
import pandas as pd

# Directory containing images
image_folder = 'data'

# Regex patterns
phone_number_pattern = r'\b1[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
account_number_pattern = r'\b(?:Account\s*(?:number|Number|No\.|[-\s]*)\s*:?\s*|Acct\s*[-\s]*)\d{1,4}(?:[-\s]?\d{1,4}){0,3}|\b\d{12,16}\b'
address_pattern = r'(?:P\.?O\.? ?Box \d{1,5}[\w\s]*|\d{1,5}[\w\s]+,\s*[A-Z]{2} \d{5}(?:-\d{4})?)|(?:[\d\w\s]+,[\s]*[A-Z]{2}[\s]*\d{5}(?:-\d{4})?)'

# Initialize lists to store results
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
    
    # Common fixes for known issues (add more as needed)
    replacements = {
        'Chases': 'Chase',
        'Uppank': 'Upbank', 
        'Pnc Access Checking Statement Pnc Bank': 'PNC Bank',  
        'Wells Fargo Simple Business Checking': 'Wells Fargo'  
        # Add more replacements as necessary
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
        
        # Extract bank name (assuming the first line is the bank name)
        text_lines = text.split('\n')
        raw_bank_name = text_lines[0].strip() if text_lines else "N/A"
        bank_name = clean_bank_name(raw_bank_name)
        
        # Extract phone numbers
        phone_numbers = re.findall(phone_number_pattern, text)
        
        # Extract account numbers
        account_number_matches = re.findall(account_number_pattern, text)
        # Get the first account number, if available
        account_number = clean_account_number(account_number_matches[0]) if account_number_matches else "N/A"
        
        # Extract addresses using regex
        addresses = re.findall(address_pattern, text)
        clean_addresses = []
        for address in addresses:
            address_lines = address.split('\n')
            clean_address = ' '.join(line.strip() for line in address_lines if line.strip())
            clean_addresses.append(clean_address)
        
        # Store results
        results.append({
            'File Name': filename,
            'Bank Name': bank_name,
            'Bank Address': clean_addresses,
            'Bank Contacts': phone_numbers,
            'Account Number': account_number,
        })

# Convert results to DataFrame
df = pd.DataFrame(results)

# Save results to CSV
df.to_csv('extracted_data.csv', index=False)

print("Data extraction completed and saved to extracted_data.csv")
