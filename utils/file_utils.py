import os

def get_pdf_files(directory):
    pdf_files = []
    for file in os.listdir(directory):
        if file.lower().endswith('.pdf'):
            pdf_files.append(file)
    return sorted(pdf_files) 