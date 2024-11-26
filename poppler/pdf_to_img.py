import time
from pdf2image import convert_from_path

start_time = time.time()

image = convert_from_path(r"C:\Users\MuraliDharan S\OneDrive\Documents\OCR_extraction.pdf", 500, poppler_path=r'D:\Program Files\poppler-24.08.0\Library\bin')
for i in range(len(image)):
    image[i].save('page'+str(i)+'.jpg', 'JPEG')

end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds")