import os
from pdf2image import convert_from_path
import pytesseract
from concurrent.futures import ThreadPoolExecutor

def ocr_page(image):
    # Customize Tesseract command for accuracy
    custom_config = r'--oem 3 --psm 4'  # Adjust based on your document's layout
    return pytesseract.image_to_string(image, config=custom_config, lang='eng')  # Specify language as needed

def pdf_to_text_parallel(pdf_path):
    images = convert_from_path(pdf_path, dpi=300, grayscale=True)
    text_fragments = []

    # Process pages in parallel
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        text_fragments = list(executor.map(ocr_page, images))

    return ''.join(text_fragments)

def convert_pdfs_in_folder_parallel(folder_path):
    pdf_paths = []

    # Walk through the directory to find all PDF files
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_paths.append(os.path.join(root, file))
    
    # Process each PDF in parallel
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        executor.map(process_pdf, pdf_paths)

def process_pdf(pdf_path):
    text = pdf_to_text_parallel(pdf_path)
    text_path = os.path.splitext(pdf_path)[0] + '.txt'
    print(f"Converting {pdf_path} to text and saving to {text_path}")
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(text)

# Start the conversion process
if __name__ == "__main__":
    convert_pdfs_in_folder_parallel('output')
