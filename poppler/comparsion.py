import time
from pdf2image import convert_from_path
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from io import BytesIO
import os
import torch
import numpy as np
from PIL import Image
from PyPDF2 import PdfReader
import asyncio
import aiofiles


def convert_pages_to_images(pdf_path, start_page, end_page, dpi=300, poppler_path=None):
    """
    Converts PDF pages to PNG byte streams for a specified range.
    Parallelized for efficiency.
    """
    try:
        images = convert_from_path(
            pdf_path, dpi=dpi, first_page=start_page, last_page=end_page, poppler_path=poppler_path
        )
        byte_streams = []
        for page_num, image in enumerate(images, start=start_page):
            byte_stream = BytesIO()
            image.save(byte_stream, format="PNG")
            byte_stream.seek(0)
            byte_streams.append((page_num, byte_stream))
        return byte_streams
    except Exception as e:
        print(f"Error converting pages {start_page}-{end_page}: {e}")
        return []


def process_batch_on_gpu(batch_streams, use_fp16=False):
    """
    Processes a batch of images on the GPU and returns processed byte streams.
    """
    try:
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA device not available.")
        
        batch_tensors = []
        page_numbers = []
        for page_number, byte_stream in batch_streams:
            byte_stream.seek(0)
            image = Image.open(byte_stream).convert("RGB")
            img_tensor = torch.from_numpy(np.array(image)).permute(2, 0, 1).float().to("cuda", non_blocking=True) / 255.0
            if use_fp16:
                img_tensor = img_tensor.half()  # Use mixed precision
            batch_tensors.append(img_tensor)
            page_numbers.append(page_number)
        
        # Stack tensors for batch processing
        batch_tensor = torch.stack(batch_tensors)
        
        # GPU processing: Resize and normalize
        processed_tensors = torch.nn.functional.interpolate(
            batch_tensor, size=(1080, 1920), mode="bilinear", align_corners=False
        )
        processed_tensors = (processed_tensors * 255).byte()

        # GPU synchronization
        torch.cuda.synchronize()

        # Convert back to PIL images and save to byte streams
        processed_streams = []
        for idx, processed_tensor in enumerate(processed_tensors):
            processed_image = processed_tensor.permute(1, 2, 0).cpu().numpy()
            processed_pil_image = Image.fromarray(processed_image)
            output_stream = BytesIO()
            processed_pil_image.save(output_stream, format="PNG")
            output_stream.seek(0)
            processed_streams.append((page_numbers[idx], output_stream))

        # GPU memory cleanup
        del batch_tensor, processed_tensors, batch_tensors
        torch.cuda.empty_cache()

        return processed_streams
    except Exception as e:
        print(f"Error processing batch on GPU: {e}")
        return []


async def save_images(processed_streams, output_dir):
    """
    Asynchronously saves processed images to disk.
    """
    os.makedirs(output_dir, exist_ok=True)
    save_tasks = []
    for page_number, byte_stream in processed_streams:
        output_file = os.path.join(output_dir, f"page_{page_number}.png")
        save_tasks.append(async_save_image(output_file, byte_stream))
    return await asyncio.gather(*save_tasks)


async def async_save_image(output_file, byte_stream):
    try:
        async with aiofiles.open(output_file, "wb") as f:
            await f.write(byte_stream.read())
        return f"Saved {output_file}"
    except Exception as e:
        return f"Error saving {output_file}: {e}"


async def process_page_range(pdf_path, start_page, end_page, dpi, poppler_path, output_dir, batch_size, use_fp16=False):
    """
    Processes a range of pages asynchronously: Converts to bytes, processes on GPU, and saves images.
    """
    byte_streams = convert_pages_to_images(pdf_path, start_page, end_page, dpi, poppler_path)
    results = []
    for i in range(0, len(byte_streams), batch_size):
        batch_streams = byte_streams[i:i + batch_size]
        processed_streams = process_batch_on_gpu(batch_streams, use_fp16)
        results.extend(await save_images(processed_streams, output_dir))
    return results


def process_page_range_wrapper(args):
    return asyncio.run(process_page_range(*args))


if __name__ == "__main__":
    pdf_path = r"C:\Users\MuraliDharan S\OneDrive\Desktop\Iterations-codility.pdf"
    poppler_path = r"D:\Program Files\poppler-24.08.0\Library\bin"
    output_dir = "output"
    batch_size = 256  # Larger batch size for better GPU utilization
    use_fp16 = True  # Enable mixed precision

    # Load the total number of pages
    with open(pdf_path, "rb") as f:
        reader = PdfReader(f)
        total_pages = len(reader.pages)

    # Define page ranges for multiprocessing
    num_workers = min(os.cpu_count(), 6)  # Limit workers to balance CPU/GPU
    chunk_size = max(1, total_pages // num_workers)
    page_ranges = [(i, min(i + chunk_size - 1, total_pages)) for i in range(1, total_pages + 1, chunk_size)]

    # Single Processing
    start_time = time.time()
    results_single = []
    for start, end in page_ranges:
        results_single.extend(asyncio.run(process_page_range(pdf_path, start, end, 300, poppler_path, output_dir, batch_size, use_fp16)))
    total_time_single = time.time() - start_time
    avg_time_single = total_time_single / total_pages
    print(f"Total time (single): {total_time_single:.2f}s, Avg per page: {avg_time_single:.2f}s")

    # Multiprocessing
    start_time = time.time()
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        args = [(pdf_path, start, end, 300, poppler_path, output_dir, batch_size, use_fp16) for start, end in page_ranges]
        results_multi = list(executor.map(process_page_range_wrapper, args))
    total_time_multi = time.time() - start_time
    avg_time_multi = total_time_multi / total_pages
    print(f"Total time (multi): {total_time_multi:.2f}s, Avg per page: {avg_time_multi:.2f}s")
