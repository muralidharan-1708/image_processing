from typing import List
from io import BytesIO
import time
from pdf2image import convert_from_path
import easyocr
import multiprocessing
import os
import asyncio


async def convert_pdf_to_io_bytes(pdf_path: str, dpi: int = 300, fmt: str = "png", poppler_path: str = None) -> List[BytesIO]:
    images = convert_from_path(pdf_path, dpi=dpi, fmt=fmt, poppler_path=poppler_path)
    buffer_list = []
    for image in images:
        buffer = BytesIO()
        image.save(buffer, format=fmt)
        buffer.seek(0)
        buffer_list.append(buffer)
    return buffer_list


def ocr_image(image_stream: BytesIO, languages: List[str] = ["en"], recog_network: str = "english_g2") -> str:
    """
    Perform OCR on the given image using EasyOCR.

    :param image_stream: BytesIO object of the image.
    :param languages: List of languages for OCR.
    :param recog_network: Recognition network to use.
    :return: Extracted text from the image.
    """
    image_stream.seek(0)
    try:
        # Initialize EasyOCR reader
        reader = easyocr.Reader(languages, recog_network=recog_network)
        result = reader.readtext(image_stream)
        return " ".join([text[1] for text in result])
    except FileNotFoundError as e:
        print(f"Error: Required model file missing. {e}")
        return ""
    except Exception as e:
        print(f"Error during OCR processing: {e}")
        return ""


def process_pdf_single(pdf_path: str, languages: List[str] = ["en"], recog_network: str = "english_g2", **kwargs) -> List[str]:
    """
    Process PDF pages sequentially for OCR.

    :param pdf_path: Path to the PDF file.
    :param languages: List of languages for OCR.
    :param recog_network: Recognition network to use.
    :return: List of extracted text for each page.
    """
    buffers = asyncio.run(convert_pdf_to_io_bytes(pdf_path, **kwargs))
    results = [ocr_image(buffer, languages, recog_network) for buffer in buffers]
    return results


def process_pdf_multi(pdf_path: str, languages: List[str] = ["en"], recog_network: str = "english_g2", **kwargs) -> List[str]:
    """
    Process PDF pages in parallel for OCR.

    :param pdf_path: Path to the PDF file.
    :param languages: List of languages for OCR.
    :param recog_network: Recognition network to use.
    :return: List of extracted text for each page.
    """
    buffers = asyncio.run(convert_pdf_to_io_bytes(pdf_path, **kwargs))
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.starmap(ocr_image, [(buffer, languages, recog_network) for buffer in buffers])
    return results


def benchmark(function, *args, iterations: int = 10, **kwargs) -> float:
    """
    Benchmark the given function.

    :param function: Function to benchmark.
    :param args: Arguments to pass to the function.
    :param iterations: Number of iterations for benchmarking.
    :return: Average execution time in seconds.
    """
    times = []
    for _ in range(iterations):
        start_time = time.time()
        function(*args, **kwargs)
        times.append(time.time() - start_time)
    return sum(times) / len(times)


if __name__ == "__main__":
    import asyncio

    # Input settings
    pdf_path = r"C:\Users\MuraliDharan S\OneDrive\Desktop\image_processing\image_processing\poppler\OCR_extraction.pdf"
    poppler_path = r"D:\Program Files\poppler-24.08.0\Library\bin"

    # Check if the required EasyOCR model files exist
    easyocr_dir = os.path.expanduser("~/.EasyOCR/user_network")
    recog_network = "latin_tamil"  # Preferred network for Tamil + Latin OCR
    if not all(
        os.path.exists(os.path.join(easyocr_dir, f"{recog_network}.{ext}"))
        for ext in ["pth", "yaml"]
    ):
        print(f"Warning: Recognition network '{recog_network}' is missing. Falling back to 'english_g2'.")
        recog_network = "english_g2"

    # Benchmark single and multi-processing modes
    avg_time_single = benchmark(process_pdf_single, pdf_path, languages=["en", "ta"], recog_network=recog_network, poppler_path=poppler_path)
    print(f"Average time (single-process): {avg_time_single:.2f} seconds")

    avg_time_multi = benchmark(process_pdf_multi, pdf_path, languages=["en", "ta"], recog_network=recog_network, poppler_path=poppler_path)
    print(f"Average time (multi-process): {avg_time_multi:.2f} seconds")
