from pdf2image import convert_from_path
from multiprocessing import Pool, cpu_count
import time

# Function to process a single page
def render_page(args):
    page_number, pdf_path, poppler_path = args
    
    # Convert a single page to an image
    images = convert_from_path(pdf_path, poppler_path=poppler_path, first_page=page_number, last_page=page_number)
    
    # Save the image as a .jpg file
    output_file = f"page_{page_number}.jpg"
    images[0].save(output_file, "JPEG")
    
    # Return a confirmation message
    return f"Saved {output_file}"

# Main code block
if __name__ == "__main__":
    # Start time for tracking execution duration
    starttime = time.time()
    
    # PDF path
    pdf_path = r"C:\Users\MuraliDharan S\OneDrive\Documents\OCR_extraction.pdf"
    
    # Define the Poppler path (update this path as per your setup)
    poppler_path = r"D:\Program Files\poppler-24.08.0\Library\bin"
    
    # Determine the total number of pages in the PDF
    total_pages = len(convert_from_path(pdf_path, poppler_path=poppler_path))
    
    # Prepare arguments for each worker (page number, pdf_path, poppler_path)
    args = [(page_number, pdf_path, poppler_path) for page_number in range(1, total_pages + 1)]
    
    # Use multiprocessing to process each page in parallel
    with Pool(cpu_count()) as pool:
        results = pool.map(render_page, args)
    
    # Print the results
    print("\n".join(results))
    
    # End time for tracking execution duration
    endtime = time.time()
    
    # Print the execution time
    print(f"\nTotal execution time: {endtime - starttime:.2f} seconds")

