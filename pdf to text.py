import os
from pdf2image import convert_from_path
import pytesseract

def pdf_to_text(pdf_path, text_path):
    """
    Convert a PDF file to text using OCR and save the text to a specified location.
    
    Args:
    - pdf_path: Path to the PDF file.
    - text_path: Path to save the output text file.
    """
    # Convert PDF to a list of images
    images = convert_from_path(pdf_path)
    
    # Initialize an empty string to store text
    text = ""
    
    # Iterate over each image and use Tesseract to extract text
    for image in images:
        text += pytesseract.image_to_string(image)
    
    # Save the extracted text to a file
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(text)

def convert_pdfs_in_folder(folder_path):
    """
    Convert all PDF files found in a folder and its subfolders to text.
    
    Args:
    - folder_path: Path to the folder to search for PDF files.
    """
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                text_path = os.path.splitext(pdf_path)[0] + '.txt'
                print(f"Converting {pdf_path} to text.")
                pdf_to_text(pdf_path, text_path)
                print(f"Text saved to {text_path}")

# Replace 'output' with the path to your specific 'output' folder if necessary
convert_pdfs_in_folder('output')
