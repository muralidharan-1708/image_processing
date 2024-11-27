from pdf2image import convert_from_path
from multiprocessing import Pool, cpu_count
import time
import os
import cupy as cp
import numpy as np
from PIL import Image

def process_image_on_gpu(np_image):
    gpu_image = cp.asarray(np_image)
    gpu_processed_image = cp.invert(gpu_image)  # Example processing: invert colors
    processed_image = cp.asnumpy(gpu_processed_image)
    return processed_image

def render_page(args):
    page_number, pdf_path, poppler_path = args
    images = convert_from_path(pdf_path, poppler_path=poppler_path, first_page=page_number, last_page=page_number)
    
    # Convert PIL image to NumPy array
    np_image = np.array(images[0])
    
    if cp.cuda.is_available():
        print(f"[INFO] Processing page {page_number} on GPU...")
        processed_image = process_image_on_gpu(np_image)
    else:
        print("[INFO] CUDA is not available. Falling back to CPU processing.")
        processed_image = np.invert(np_image)
    
    # Convert back to PIL image and save
    pil_image = Image.fromarray(processed_image)
    output_file = f"page_{page_number}.jpg"
    pil_image.save(output_file, "JPEG")
    return f"Saved {output_file}"

if __name__ == "__main__":
    # Check CUDA availability
    if cp.cuda.is_available():
        print("CUDA is available. The GPU will be used for computation.")
    else:
        print("CUDA is not available. The code will run on CPU.")
    
    starttime = time.time()
    pdf_path = r"C:\Users\MuraliDharan S\OneDrive\Desktop\image_processing\image_processing\poppler\OCR_extraction.pdf"
    poppler_path = r"D:\Program Files\poppler-24.08.0\Library\bin"
    
    # Verify the file exists
    if not os.path.exists(pdf_path):
        print(f"Error: The file '{pdf_path}' does not exist.")
    else:
        try:
            total_pages = len(convert_from_path(pdf_path, poppler_path=poppler_path))
            args = [(page_number, pdf_path, poppler_path) for page_number in range(1, total_pages + 1)]
            
            with Pool(cpu_count()) as pool:
                results = pool.map(render_page, args)
            
            print("\n".join(results))
        except Exception as e:
            print(f"Error processing PDF: {e}")
    
    endtime = time.time()
    print(f"\nTotal execution time: {endtime - starttime:.2f} seconds")
