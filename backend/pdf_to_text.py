import PyPDF2

def convert_pdf_to_text(pdf_file):
    text = ""
    reader = PyPDF2.PdfReader(pdf_file)
    for page in reader.pages:
        text += page.extract_text() + "\n"  # Append text from each page
    return text


if __name__ == "__main__":
    print(convert_pdf_to_text('/home/kali/Downloads/problem-statements.pdf'))