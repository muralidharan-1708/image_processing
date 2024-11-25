from pdf2image import convert_from_path

image = convert_from_path('NPTEL_2024.pdf', 500,poppler_path=r'D:\Program Files\poppler-24.08.0\Library\bin')
for i in range(len(image)):
    image[i].save('page'+str(i)+'.jpg', 'JPEG')