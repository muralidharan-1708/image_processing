**PDF Processing with Poppler, pdf2image, and Pillow**
This project demonstrates how to convert PDF files into images, extract text from PDF pages, and utilize multiprocessing to speed up image rendering using Poppler, pdf2image, and Pillow (PIL).

**Prerequisites**
# 1. Python Installation
    `Ensure you have Python installed (preferably Python 3.7+).`
# 2. Install Required Python Libraries
    `Run the following command to install dependencies:
        `pip install pdf2image Pillow PyMuPDF``
# 3. Install Poppler
    `Poppler is a PDF rendering library required by pdf2image.`

# Steps to Install Poppler:
    1.Download the Poppler library for Windows from Poppler for Windows.
    2.Extract the downloaded .zip file to a folder (e.g., C:\Program Files\poppler).
    3.Add the bin directory of Poppler to your system's PATH or specify it in your code:
        Example: > C:\Program Files\poppler\bin

**Features**
# 1.Convert PDF Pages to Images
    Render high-quality images from PDF pages using pdf2image.
# 2.Extract Text from PDF Pages
    Use PyMuPDF (fitz) to extract text content from each page of the PDF.
# 3.Save Processed Pages as Images
    Save PDF pages as .jpg or .png files using Pillow (PIL).
# 4.Multiprocessing for Large PDFs
    Leverage multiprocessing to speed up rendering for PDFs with many pages.
