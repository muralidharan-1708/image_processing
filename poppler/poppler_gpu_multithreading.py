from pdf2image import convert_from_path
import torch
import torchvision.transforms as T
import numpy as np
from PIL import Image
import os
import time
from concurrent.futures import ThreadPoolExecutor

def render_pages_with_poppler(pdf_path, page_range, poppler_path):
    """Render a range of PDF pages using Poppler and return them as GPU tensors."""
    try:
        # Render specified pages to images
        images = convert_from_path(pdf_path, poppler_path=poppler_path, first_page=page_range[0], last_page=page_range[1])
        tensors = []
        for img in images:
            raw_image = np.array(img)
            tensor_image = torch.from_numpy(raw_image).permute(2, 0, 1).to('cuda')  # (C, H, W)
            tensors.append(tensor_image)
        return tensors
    except Exception as e:
        return f"Error rendering pages {page_range}: {e}"

def process_images_on_gpu(tensor_images, page_range):
    """Perform all processing on GPU and save the images."""
    results = []
    try:
        transform = T.Compose([
            T.Resize((1080, 1920)),  # Resize to 1080p
            T.Normalize((0.5,), (0.5,)),  # Normalize to range [-1, 1]
        ])
        for i, tensor_image in enumerate(tensor_images):
            page_number = page_range[0] + i
            processed_image = transform(tensor_image.float() / 255)  # Normalize to [0, 1]

            # Save the processed image
            output_image = (processed_image * 255).byte().permute(1, 2, 0).cpu().numpy()  # Convert back to NumPy
            output_file = f"page_{page_number}_gpu.jpg"
            Image.fromarray(output_image).save(output_file)
            results.append(f"Saved {output_file} on GPU")
    except Exception as e:
        results.append(f"Error processing pages {page_range}: {e}")
    return results

def process_page_batch(args):
    """Combine rendering and processing for a batch of pages."""
    page_range, pdf_path, poppler_path = args
    tensors = render_pages_with_poppler(pdf_path, page_range, poppler_path)
    if isinstance(tensors, str):  # Check for rendering errors
        return [tensors]
    return process_images_on_gpu(tensors, page_range)

if __name__ == "__main__":
    # Set up paths
    pdf_path = r"C:\Users\MuraliDharan S\OneDrive\Desktop\Iterations-codility.pdf"
    poppler_path = r"D:\Program Files\poppler-24.08.0\Library\bin"

    # Debugging: Check file existence
    print(f"Looking for file at: {pdf_path}")
    if not os.path.exists(pdf_path):
        print("File not found! Check the path and try again.")
        exit()

    # Process PDF
    start_time = time.time()
    try:
        total_pages = len(convert_from_path(pdf_path, poppler_path=poppler_path))
        print(f"Total pages in the PDF: {total_pages}")
    except Exception as e:
        print(f"Error opening PDF file: {e}")
        exit()

    # Prepare arguments for parallel processing in batches
    batch_size = 2  # Number of pages per batch
    args = [
        ((i, min(i + batch_size - 1, total_pages)), pdf_path, poppler_path)
        for i in range(1, total_pages + 1, batch_size)
    ]

    # Use ThreadPoolExecutor for parallel processing
    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:  # Adjust max_workers based on GPU capacity
        for batch_results in executor.map(process_page_batch, args):
            results.extend(batch_results)

    # Print results
    print("\n".join(results))
    print(f"\nTotal execution time: {time.time() - start_time:.2f} seconds")
