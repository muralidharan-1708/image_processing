import time
from pdf2image import convert_from_path
import torch
from torchvision import transforms
from PIL import Image
import concurrent.futures

# Configuration
pdf_path = "OCR_extraction.pdf"
poppler_path = r"D:\Program Files\poppler-24.08.0\Library\bin"
dpi = 300
first_page = 1
last_page = 2

device = 'cuda' if torch.cuda.is_available() else 'cpu'
if torch.cuda.is_available():
    print("Using CUDA")
else:
    print("CUDA not available")

start_time = time.time()

# Convert PDF to images
images = convert_from_path(pdf_path, poppler_path=poppler_path, dpi=dpi, first_page=first_page, last_page=last_page)

# Define a transform to convert images to tensors
transform = transforms.ToTensor()

def process_image(i, image):
    image_start_time = time.time()

    # Convert image to tensor and move to GPU if available
    image_tensor = transform(image).to(device)

    # Apply any GPU processing here if needed (e.g., filters or enhancements)

    # Save processed image directly from tensor (avoiding unnecessary CPU conversions)
    output_image = transforms.ToPILImage()(image_tensor.cpu())
    output_image.save(f'page_{i + 1}.png', quality=95)

    return time.time() - image_start_time

# Process images in parallel using ThreadPoolExecutor
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(process_image, i, image) for i, image in enumerate(images)]
    times = [future.result() for future in concurrent.futures.as_completed(futures)]

end_time = time.time()
execution_time = end_time - start_time
average_time = sum(times) / len(times)

print(f"Execution time: {execution_time:.2f} seconds")
print(f"Average time per image: {average_time:.2f} seconds")
print(f"Total number of pages processed: {len(images)}")