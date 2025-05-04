import textract
PDF_FILE_PATH = "./_docs_dir/sonata.pdf"
text_content = textract.process(PDF_FILE_PATH)
decoded_text = text_content.decode('utf-8')
with open("extracted_text.txt", "w", encoding="utf-8") as f:
    f.write(decoded_text)
print("Extracted text saved to extracted_text.txt")