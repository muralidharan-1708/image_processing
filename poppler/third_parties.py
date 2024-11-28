import time
import cupy as cp  # CuPy for GPU arrays (CUDA)
from pdf2image import convert_from_path
from PIL import Image
import concurrent.futures  # For parallel file saving
import cv2
import numpy as np

# Convert PDF pages to images
def convert_pdf_to_image(pdf_path, first_page, last_page, poppler_path):
    try:
        images = convert_from_path(pdf_path, poppler_path=poppler_path, first_page=first_page, last_page=last_page)
        image_arrays = [np.array(img) for img in images]
        return image_arrays
    except Exception as e:
        return f"Error processing pages {first_page}-{last_page}: {e}"

# Process each image on GPU using CuPy (CUDA arrays)
def process_image_on_gpu(image_array, page_number):
    try:
        # Convert image to a CuPy array and send it to GPU
        img_cp = cp.asarray(image_array).astype(cp.float32) / 255.0  # Normalize to [0, 1]

        # Resize the image on the GPU using OpenCV (cv2.resize() - faster GPU resizing)
        img_resized = cv2.resize(cp.asnumpy(img_cp), (1920, 1080), interpolation=cv2.INTER_LINEAR)  # Resize to 1080p

        # Convert the resized image back to NumPy and then to uint8 for saving
        img_resized_cpu = np.uint8(img_resized * 255)

        # Save the processed image in a separate thread to optimize I/O
        output_file = f"page_{page_number}_gpu_processed.jpg"
        Image.fromarray(img_resized_cpu).save(output_file)

        return f"Processed and saved {output_file}"

    except Exception as e:
        return f"Error processing page {page_number}: {e}"

# Function to handle file saving in parallel
def save_file_concurrently(results):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(result) for result in results]
        concurrent.futures.wait(futures)

# Main execution logic
def main():
    pdf_path = r"C:\Users\MuraliDharan S\OneDrive\Desktop\Iterations-codility.pdf"
    poppler_path = r"D:\Program Files\poppler-24.08.0\Library\bin"

    start_time = time.time()

    # Get the total number of pages in the PDF
    try:
        total_pages = len(convert_from_path(pdf_path, poppler_path=poppler_path))
        print(f"Total pages in the PDF: {total_pages}")
    except Exception as e:
        print(f"Error opening PDF file: {e}")
        return

    # Process each page using CuPy and GPU
    results = []
    image_arrays = convert_pdf_to_image(pdf_path, 1, total_pages, poppler_path)

    for idx, image_array in enumerate(image_arrays):
        page_number = idx + 1
        result = process_image_on_gpu(image_array, page_number)
        results.append(result)

    # Save all files in parallel to reduce I/O wait time
    save_file_concurrently(results)

    # Print results and execution time
    print("\n".join(results))
    print(f"\nTotal execution time: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
