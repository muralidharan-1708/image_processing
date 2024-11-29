import time
from pdf2image import convert_from_path
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO
import os


def batch_convert_to_bytes(pdf_path, page_range, dpi=300, poppler_path=None):
    """
    Convert a range of PDF pages to byte streams of images.
    """
    try:
        images = convert_from_path(
            pdf_path, dpi=dpi, first_page=page_range[0], last_page=page_range[1], poppler_path=poppler_path
        )
        byte_streams = []
        for i, image in enumerate(images, start=page_range[0]):
            with BytesIO() as byte_stream:
                image.save(byte_stream, format="PNG")
                byte_stream.seek(0)
                byte_streams.append((i, byte_stream.read()))  # Pass bytes directly
        return byte_streams
    except Exception as e:
        return []


def save_image_from_bytes(page_number, byte_data, output_dir="output"):
    """
    Save a byte stream of an image to disk.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"page_{page_number}.png")
    try:
        with open(output_file, "wb") as f:
            f.write(byte_data)
        return f"Saved {output_file}"
    except Exception as e:
        return f"Error saving page {page_number}: {e}"


def process_batch(pdf_path, page_range, dpi, poppler_path, output_dir="output"):
    """
    Process a batch of pages: convert to bytes and save as images.
    """
    results = []
    byte_streams = batch_convert_to_bytes(pdf_path, page_range, dpi, poppler_path)
    for page_number, byte_data in byte_streams:
        results.append(save_image_from_bytes(page_number, byte_data, output_dir))
    return results


if __name__ == "__main__":
    pdf_path = r"C:\Users\MuraliDharan S\OneDrive\Desktop\Iterations-codility.pdf"
    total_pages = 10
    poppler_path = r"D:\Program Files\poppler-24.08.0\Library\bin"
    batch_size = 2  # Process multiple pages per task to reduce overhead
    page_ranges = [
        (i, min(i + batch_size - 1, total_pages)) for i in range(1, total_pages + 1, batch_size)
    ]

    # Single Processing
    starttime = time.time()
    results_single = []
    for page_range in page_ranges:
        results_single.extend(process_batch(pdf_path, page_range, 300, poppler_path))
    endtime = time.time()
    total_time_single = endtime - starttime
    avg_time_single = total_time_single / total_pages
    print("\n".join(results_single))
    print(f"\nTotal execution time (single processing): {total_time_single:.2f} seconds")
    print(f"Average time per page (single processing): {avg_time_single:.2f} seconds")

    # Multiprocessing
    starttime = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:  # Use 4 workers (adjust based on your CPU)
        results_multi = list(
            executor.map(
                process_batch,
                [pdf_path] * len(page_ranges),
                page_ranges,
                [300] * len(page_ranges),
                [poppler_path] * len(page_ranges),
                ["output"] * len(page_ranges),
            )
        )
    results_multi_flat = [item for sublist in results_multi for item in sublist]
    endtime = time.time()
    total_time_multi = endtime - starttime
    avg_time_multi = total_time_multi / total_pages
    print("\n".join(results_multi_flat))
    print(f"\nTotal execution time (multiprocessing): {total_time_multi:.2f} seconds")
    print(f"Average time per page (multiprocessing): {avg_time_multi:.2f} seconds")
