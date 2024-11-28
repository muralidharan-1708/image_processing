import time
from pdf2image import convert_from_path
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO
import os
import torch
import numpy as np
from PIL import Image
from PyPDF2 import PdfReader


def batch_convert_to_bytes(pdf_path, page_range, dpi=300, poppler_path=None):
    """
    Converts a range of PDF pages to PNG format as byte streams.
    """
    try:
        images = convert_from_path(
            pdf_path, dpi=dpi, first_page=page_range[0], last_page=page_range[1], poppler_path=poppler_path
        )
        byte_streams = []
        for i, image in enumerate(images, start=page_range[0]):
            byte_stream = BytesIO()
            image.save(byte_stream, format="PNG")
            byte_stream.seek(0)
            byte_streams.append((i, byte_stream))
        return byte_streams
    except Exception:
        return []


def process_image_on_gpu(byte_stream: BytesIO) -> BytesIO:
    """
    Processes an image on the GPU (resize and normalize) and returns a processed BytesIO stream.
    """
    try:
        byte_stream.seek(0)
        image = Image.open(byte_stream).convert("RGB")
        
        # Convert image to PyTorch tensor and send to GPU
        img_tensor = torch.from_numpy(np.array(image)).permute(2, 0, 1).float().to("cuda") / 255.0
        
        # Resize and normalize on GPU
        processed_tensor = torch.nn.functional.interpolate(
            img_tensor.unsqueeze(0), size=(1080, 1920), mode="bilinear", align_corners=False
        ).squeeze(0)
        processed_tensor = (processed_tensor * 255).byte()
        
        # Convert back to PIL image
        processed_image = processed_tensor.permute(1, 2, 0).cpu().numpy()
        processed_pil_image = Image.fromarray(processed_image)

        # Save to BytesIO stream
        output_stream = BytesIO()
        processed_pil_image.save(output_stream, format="PNG")
        output_stream.seek(0)
        return output_stream
    except Exception as e:
        print(f"Error processing image on GPU: {e}")
        return None


def save_image_from_bytes(page_number, byte_stream, output_dir="output"):
    """
    Saves the processed image from a BytesIO stream to a file.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"page_{page_number}.png")
    try:
        with open(output_file, "wb") as f:
            f.write(byte_stream.read())
        return f"Saved {output_file}"
    except Exception as e:
        return f"Error saving page {page_number}: {e}"


def process_page_range(args):
    """
    Processes a range of pages: Converts to bytes, processes on GPU, and saves the results.
    """
    pdf_path, page_range, dpi, poppler_path = args
    results = []
    byte_streams = batch_convert_to_bytes(pdf_path, page_range, dpi, poppler_path)
    for page_number, byte_stream in byte_streams:
        gpu_processed_stream = process_image_on_gpu(byte_stream)
        if gpu_processed_stream is not None:
            results.append(save_image_from_bytes(page_number, gpu_processed_stream))
        else:
            results.append(f"Failed to process page {page_number}")
    return results


if __name__ == "__main__":
    pdf_path =  r"C:\Users\MuraliDharan S\OneDrive\Desktop\Iterations-codility.pdf"
    with open(pdf_path, "rb") as f:
        reader = PdfReader(f)
        total_pages = len(reader.pages)
    poppler_path = r"D:\Program Files\poppler-24.08.0\Library\bin"
    page_ranges = [(i, min(i, total_pages)) for i in range(1, total_pages + 1)]

    # Single Processing
    starttime = time.time()
    results_single = []
    for page_range in page_ranges:
        results_single.extend(process_page_range((pdf_path, page_range, 300, poppler_path)))
    endtime = time.time()
    total_time_single = endtime - starttime
    avg_time_single = total_time_single / total_pages
    print("\n".join(results_single))
    print(f"\nTotal execution time (single processing): {total_time_single:.2f} seconds")
    print(f"Average time per page (single processing): {avg_time_single:.2f} seconds")

    # Multiprocessing
    starttime = time.time()
    with ProcessPoolExecutor() as executor:
        results_multi = list(executor.map(process_page_range, [(pdf_path, page_range, 300, poppler_path) for page_range in page_ranges]))
    results_multi_flat = [item for sublist in results_multi for item in sublist]
    endtime = time.time()
    total_time_multi = endtime - starttime
    avg_time_multi = total_time_multi / total_pages
    print("\n".join(results_multi_flat))
    print(f"\nTotal execution time (multiprocessing): {total_time_multi:.2f} seconds")
    print(f"Average time per page (multiprocessing): {avg_time_multi:.2f} seconds")
