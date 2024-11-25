from pdf2image import convert_from_path
import fitz  # PyMuPDF for text extraction

pdf_path = "NPTEL_2024.pdf"
images = convert_from_path(pdf_path, poppler_path=r"D:\Program Files\poppler-24.08.0\Library\bin")

for i in range(len(images)):
    images[i].save('page'+str(i)+'.jpg', 'JPEG')
    
doc = fitz.open(pdf_path)
for i in range(len(doc)):
    page = doc.load_page(i)
    text = page.get_text()
    print(text)
