import fitz  # PyMuPDF
import torch
import torchvision.transforms as T
import numpy as np
from PIL import Image
import os
import time

def render_page_to_gpu(pdf_path, page_number):
    """Render a PDF page directly onto GPU."""
    try:
        # Load PDF and select page
        pdf_document = fitz.open(pdf_path)
        page = pdf_document[page_number - 1]  # Zero-based index

        # Render page to raw pixel data (as an array)
        pix = page.get_pixmap(alpha=False)  # Render without transparency
        raw_image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)  # (H, W, C)

        # Move image data to GPU
        tensor_image = torch.from_numpy(raw_image).permute(2, 0, 1).to('cuda')  # (C, H, W)

        # Close PDF resources
        pdf_document.close()

        return tensor_image
    except Exception as e:
        return f"Error rendering page {page_number}: {e}"

def process_image_on_gpu(tensor_image, page_number):
    """Perform all processing on GPU."""
    try:
        # Example processing: resize and normalize
        transform = T.Compose([
            T.Resize((1080, 1920)),  # Resize to 1080p
            T.Normalize((0.5,), (0.5,)),  # Normalize to range [-1, 1]
        ])
        processed_image = transform(tensor_image.float() / 255)  # Ensure data is normalized to [0, 1]

        # Save the processed image back to disk
        output_image = (processed_image * 255).byte().permute(1, 2, 0).cpu().numpy()  # Back to (H, W, C) on CPU for saving
        output_file = f"page_{page_number}_gpu.jpg"
        Image.fromarray(output_image).save(output_file)
        return f"Saved {output_file} on GPU"
    except Exception as e:
        return f"Error processing page {page_number} on GPU: {e}"

if __name__ == "__main__":
    # Set up PDF path
    pdf_path = r"C:\Users\MuraliDharan S\OneDrive\Desktop\image_processing\image_processing\poppler\OCR_extraction.pdf"

    # Debugging: Check file existence
    print(f"Looking for file at: {pdf_path}")
    if not os.path.exists(pdf_path):
        print("File not found! Check the path and try again.")
        exit()

    # Process PDF
    start_time = time.time()
    try:
        total_pages = fitz.open(pdf_path).page_count
        print(f"Total pages in the PDF: {total_pages}")
    except Exception as e:
        print(f"Error opening PDF file: {e}")
        exit()

    # Process each page
    results = []
    for page_number in range(1, total_pages + 1):
        try:
            tensor_image = render_page_to_gpu(pdf_path, page_number)  # Render on GPU
            if isinstance(tensor_image, str):  # Error handling
                results.append(tensor_image)
                continue
            result = process_image_on_gpu(tensor_image, page_number)  # Process on GPU
            results.append(result)
        except Exception as e:
            results.append(f"Error on page {page_number}: {e}")

    # Print results
    print("\n".join(results))
    print(f"\nTotal execution time: {time.time() - start_time:.2f} seconds")
