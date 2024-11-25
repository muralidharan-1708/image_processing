from PIL import Image
img = Image.open(r"C:\Users\MuraliDharan S\OneDrive\Desktop\HTML-CSS BEG\images\shinchan.jpg")
print(img.width,img.height)
img.show()
img = img.resize((int(img.width/2),int(img.height/2)),resample=Image.LANCZOS,box=(30,30,100,100)) #box=(left,upper,right,lower) LANCZOS = best quality
#resample = Image.NEAREST, Image.BOX, Image.BILINEAR, Image.HAMMING, Image.BICUBIC, Image.LANCZOS
print(img.width,img.height)
img.show()