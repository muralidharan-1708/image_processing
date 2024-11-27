from pdf2image import convert_from_path
from concurrent.futures import ThreadPoolExecutor
import time

def render_page(args):
    page_number, pdf_path, poppler_path = args
    try:
        images = convert_from_path(pdf_path, poppler_path=poppler_path, first_page=page_number, last_page=page_number)
        output_file = f"page_{page_number}.jpg"
        images[0].save(output_file, "JPEG")
        return f"Saved {output_file}"
    except Exception as e:
        return f"Error processing page {page_number}: {e}"

if __name__ == "__main__":
    starttime = time.time()
    pdf_path =r"C:\Users\MuraliDharan S\OneDrive\Desktop\Iterations-codility.pdf"
    poppler_path = r"D:\Program Files\poppler-24.08.0\Library\bin"
    
    total_pages = len(convert_from_path(pdf_path, poppler_path=poppler_path))
    
    args = [(page_number, pdf_path, poppler_path) for page_number in range(1, total_pages + 1)]
    
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(render_page, args))
    
    print("\n".join(results))
    
    endtime = time.time()
    print(f"\nTotal execution time: {endtime - starttime:.2f} seconds")