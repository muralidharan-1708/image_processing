from PIL import Image
img = Image.open(r"C:\Users\MuraliDharan S\OneDrive\Desktop\HTML-CSS BEG\images\tessa.jpg")
imgcrop = img.crop((60,60,400,400)) #box=(left,upper,right,lower
imgcrop.show()
