import os
import PyPDF2

UPLOAD_DIR = "pdf"


def save_uploaded_file(file_contents, filename):
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(file_contents)
    return filepath


def read_pdf_text(file_contents):
    pdf_reader = PyPDF2.PdfReader(file_contents)
    text = ""
    for page_num in range(pdf_reader.numPages):
        page = pdf_reader.getPage(page_num)
        text += page.extractText()
    return text


def delete_file(filepath):
    try:
        os.remove(filepath)
        return True
    except FileNotFoundError:
        return False
