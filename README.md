# Bank Data Extraction Script

This Python script extracts bank-related information from images of documents using Optical Character Recognition (OCR). It processes images to identify and extract bank names, phone numbers, account numbers, and addresses, and then saves this information into a CSV file.

## Features

- **Extract Bank Names**: Identifies and cleans up bank names from the first line of text in the image.
- **Extract Phone Numbers**: Uses regular expressions to find phone numbers in various formats.
- **Extract Account Numbers**: Identifies and cleans up account numbers, focusing on the first account number found.
- **Extract Addresses**: Extracts and formats addresses from the image text.
- **Save to CSV**: Outputs the extracted data into a CSV file for further analysis.

## Requirements

- Python 3.x
- `pytesseract` (Python wrapper for Tesseract OCR)
- `Pillow` (Python Imaging Library)
- `pandas` (Data manipulation library)
- Tesseract-OCR installed on your system

## Installation

1. **Install Python**: Ensure Python 3.x is installed on your system. You can download it from [python.org](https://www.python.org/).

2. **Install Required Packages**: Use pip to install the necessary Python libraries:

   
    ***pip install pytesseract pillow pandas***
    

3. **Install Tesseract-OCR**: Follow the installation instructions for Tesseract-OCR based on your operating system:

    - **Windows**: Download the installer from [GitHub](https://github.com/tesseract-ocr/tesseract) and follow the installation instructions.
    - **macOS**: Install via Homebrew:


      ***brew install tesseract***
   

    - **Linux**: Install via package manager (e.g., `apt` for Debian/Ubuntu):


      ***sudo apt-get install tesseract-ocr***
      

## Usage

1. **Prepare the Image Folder**: Place your image files in a folder named `data` in the same directory as the script. Ensure that your images are in `.png`, `.jpg`, or `.jpeg` formats.

2. **Run the Script**: Execute the script from the command line:

 
    ***python extract_data.py***
  

    The script will process each image in the `data` folder, extract relevant information, and save the results to a CSV file named `extracted_data.csv`.

3. **Check the Results**: After running the script, you can find the output in the `extracted_data.csv` file in the same directory. This CSV file will contain columns for the file name, bank name, bank address, bank contacts (phone numbers), and account number.

## Customization

You can modify the regex patterns in the script to better match the specific formats of phone numbers, account numbers, or addresses in your documents. Adjust the `clean_account_number` and `clean_bank_name` functions to refine how data is cleaned and standardized.
