# from pdf2image import convert_from_path
# from multiprocessing import Pool, cpu_count
# import time

# # Function to process a single page
# def render_page(args):
#     page_number, pdf_path, poppler_path = args
    
#     # Convert a single page to an image
#     images = convert_from_path(pdf_path, poppler_path=poppler_path, first_page=page_number, last_page=page_number)
    
#     # Save the image as a .jpg file
#     output_file = f"page_{page_number}.jpg"
#     images[0].save(output_file, "JPEG")
    
#     # Return a confirmation message
#     return f"Saved {output_file}"

# # Main code block
# if __name__ == "__main__":
#     # Start time for tracking execution duration
#     starttime = time.time()
    
#     # PDF path
#     pdf_path = r"C:\Users\MuraliDharan S\OneDrive\Documents\OCR_extraction.pdf"
    
#     # Define the Poppler path (update this path as per your setup)
#     poppler_path = r"D:\Program Files\poppler-24.08.0\Library\bin"
    
#     # Determine the total number of pages in the PDF
#     total_pages = len(convert_from_path(pdf_path, poppler_path=poppler_path))
    
#     # Prepare arguments for each worker (page number, pdf_path, poppler_path)
#     args = [(page_number, pdf_path, poppler_path) for page_number in range(1, total_pages + 1)]
    
#     # Use multiprocessing to process each page in parallel
#     with Pool(cpu_count()) as pool:
#         results = pool.map(render_page, args)
    
#     # Print the results
#     print("\n".join(results))
    
#     # End time for tracking execution duration
#     endtime = time.time()
    
#     # Print the execution time
#     print(f"\nTotal execution time: {endtime - starttime:.2f} seconds")


from pdf2image import convert_from_path
import multiprocessing
import easyocr
from tqdm import tqdm
import time

def ocr_on_image(image, reader):
    return reader.readtext(image)

def extract_images_from_pdf(pdf_path):
    return convert_from_path(pdf_path, poppler_path=r"D:\Program Files\poppler-24.08.0\Library\bin")

def process_pdf(pdf_path, reader):
    images = extract_images_from_pdf(pdf_path)
    ocr_results = []
    for image in images:
        ocr_results.append(ocr_on_image(image, reader))
    return ocr_results

def process_pdfs_in_parallel(pdf_paths, reader):
    NCPU = multiprocessing.cpu_count() - 2  # Use all but 2 cores for optimal performance
    with multiprocessing.Pool(processes=NCPU) as pool:
        results = list(tqdm(pool.imap(lambda pdf: process_pdf(pdf, reader), pdf_paths), total=len(pdf_paths)))
    return results

if __name__ == "__main__":
    reader = easyocr.Reader(['en'])

    pdf_files = [
        r"C:\Users\MuraliDharan S\OneDrive\Documents\OCR_extraction.pdf", 
        r"poppler/NPTEL_2024.pdf"
    ]
    
    processed_data = process_pdfs_in_parallel(pdf_files, reader)
    print(processed_data)

