import time
from pdf2image import convert_from_path
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
import torch
from PIL import Image
import numpy as np

def convert_pdf_to_images(pdf_path, dpi=300, poppler_path=None):
    try:
        images = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)
        return images
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return []

def gpu_process_image(byte_stream: BytesIO, use_gpu=True) -> BytesIO:
    try:
        byte_stream.seek(0)
        with Image.open(byte_stream) as image:
            image = image.convert("RGB")

        device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        print(f"Processing image on {device.upper()}")

        img_tensor = torch.from_numpy(np.array(image)).permute(2, 0, 1).float().to(device) / 255.0

        processed_tensor = torch.nn.functional.interpolate(
            img_tensor.unsqueeze(0), size=(1080, 1920), mode="bilinear", align_corners=False
        ).squeeze(0)
        processed_tensor = (processed_tensor * 255).byte()

        processed_image = processed_tensor.permute(1, 2, 0).cpu().numpy()
        processed_pil_image = Image.fromarray(processed_image)

        with BytesIO() as output_stream:
            processed_pil_image.save(output_stream, format="PNG")
            output_stream.seek(0)
            return BytesIO(output_stream.read())
    except Exception as e:
        print(f"Error processing image on GPU: {e}")
        return None

def save_image(image_bytes: BytesIO, output_file: str):
    try:
        with open(output_file, "wb") as f:
            f.write(image_bytes.read())
        return f"Saved {output_file}"
    except Exception as e:
        print(f"Error saving {output_file}: {e}")
        return None

def process_image(page_number, image, use_gpu):
    try:
        with BytesIO() as image_stream:
            image.save(image_stream, format="PNG")
            image_stream.seek(0)
            gpu_processed_stream = gpu_process_image(image_stream, use_gpu)
            if gpu_processed_stream:
                output_file = f"page_{page_number}_processed.png"
                return save_image(gpu_processed_stream, output_file)
            else:
                return f"Failed to process page {page_number}"
    except Exception as e:
        return f"Error processing page {page_number}: {e}"

if __name__ == "__main__":
    pdf_path = r"C:\Users\MuraliDharan S\OneDrive\Desktop\Iterations-codility.pdf"
    poppler_path = r"D:\Program Files\poppler-24.08.0\Library\bin"

    use_gpu = True

    print("Converting PDF to images...")
    starttime = time.time()
    images = convert_pdf_to_images(pdf_path, dpi=300, poppler_path=poppler_path)
    for i, image in enumerate(images):
        image.save(f"page_{i + 1}.png", "PNG")
    total_time = time.time() - starttime
    avg_time = total_time / len(images)
    print(f"Total time for converting PDF to images: {total_time:.2f} seconds")
    print(f"Average time per page for converting PDF to images: {avg_time:.2f} seconds")

    print("\nProcessing images with ThreadPoolExecutor...")
    starttime = time.time()

    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_image, page_number, image, use_gpu): page_number for page_number, image in enumerate(images, start=1)}
        for future in as_completed(futures):
            page_number = futures[future]
            try:
                result = future.result()
                results.append((page_number, result))
            except Exception as e:
                results.append((page_number, f"Error processing page {page_number}: {e}"))

    for page_number, result in results:
        print(f"Page {page_number}: {result}")

    endtime = time.time()
    total_time_multiprocessing = endtime - starttime
    avg_time_multiprocessing = total_time_multiprocessing / len(images)
    print(f"\nTotal execution time (ThreadPoolExecutor): {total_time_multiprocessing:.2f} seconds")
    print(f"Average time per page (ThreadPoolExecutor): {avg_time_multiprocessing:.2f} seconds")
