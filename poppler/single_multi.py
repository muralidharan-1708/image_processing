import time
from pdf2image import convert_from_path
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import torch
from PIL import Image
import numpy as np


def convert_pdf_page_to_bytes(pdf_path, page_number, dpi=300, poppler_path=None) -> BytesIO:
    """
    Converts a single PDF page to an image and returns it as a BytesIO stream.
    """
    try:
        images = convert_from_path(
            pdf_path, dpi=dpi, first_page=page_number, last_page=page_number, poppler_path=poppler_path
        )
        if not images:
            raise ValueError(f"Page {page_number} could not be converted.")
        byte_stream = BytesIO()
        images[0].save(byte_stream, format="PNG")
        byte_stream.seek(0)
        return byte_stream
    except Exception as e:
        print(f"Error converting page {page_number}: {e}")
        return None


def gpu_process_image(byte_stream: BytesIO) -> BytesIO:
    """
    Processes an image on the GPU and returns it as a BytesIO stream.
    """
    try:
        byte_stream.seek(0)
        image = Image.open(byte_stream).convert("RGB")

        img_tensor = torch.from_numpy(np.array(image)).permute(2, 0, 1).float().to("cuda") / 255.0

        processed_tensor = torch.nn.functional.interpolate(
            img_tensor.unsqueeze(0), size=(1080, 1920), mode="bilinear", align_corners=False
        ).squeeze(0)
        processed_tensor = (processed_tensor * 255).byte()

        processed_image = processed_tensor.permute(1, 2, 0).cpu().numpy()
        processed_pil_image = Image.fromarray(processed_image)

        output_stream = BytesIO()
        processed_pil_image.save(output_stream, format="PNG")
        output_stream.seek(0)
        return output_stream
    except Exception as e:
        print(f"Error processing image on GPU: {e}")
        return None


def save_image_bytes(byte_stream: BytesIO, output_file: str):
    """
    Saves the processed image from a BytesIO stream to a file.
    """
    try:
        with open(output_file, "wb") as f:
            f.write(byte_stream.read())
        return f"Saved {output_file}"
    except Exception as e:
        print(f"Error saving {output_file}: {e}")
        return None


def process_page(pdf_path, page_number, dpi=300, poppler_path=None):
    """
    Processes a single PDF page: Converts it to an image, applies GPU processing, and saves the output.
    """
    byte_stream = convert_pdf_page_to_bytes(pdf_path, page_number, dpi, poppler_path)
    if byte_stream is not None:
        gpu_processed_stream = gpu_process_image(byte_stream)
        if gpu_processed_stream is not None:
            output_file = f"page_{page_number}_processed.png"
            result = save_image_bytes(gpu_processed_stream, output_file)
            return result if result is not None else f"Failed to save page {page_number}"
    return f"Failed to process page {page_number}"


def process_page_wrapper(args):
    return process_page(*args)


if __name__ == "__main__":
    pdf_path = r"C:\Users\MuraliDharan S\OneDrive\Desktop\Iterations-codility.pdf"
    total_pages = 4
    poppler_path = r"D:\Program Files\poppler-24.08.0\Library\bin"
    args = [(pdf_path, page_number, 300, poppler_path) for page_number in range(1, total_pages + 1)]

    starttime = time.time()
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(process_page_wrapper, args))
    print("\n".join(results))
    endtime = time.time()
    print(f"\nTotal execution time (multi-threaded): {endtime - starttime:.2f} seconds")

    starttime = time.time()
    results = []
    for page_number in range(1, total_pages + 1):
        result = process_page(pdf_path, page_number, dpi=300, poppler_path=poppler_path)
        results.append(result)
    print("\n".join(results))
    endtime = time.time()
    print(f"\nTotal execution time (single-threaded): {endtime - starttime:.2f} seconds")
