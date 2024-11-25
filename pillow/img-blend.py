from PIL import Image
img1 = Image.open(r"C:\Users\MuraliDharan S\OneDrive\Desktop\HTML-CSS BEG\images\vjsiddu.webp")
img2 = Image.open(r"C:\Users\MuraliDharan S\OneDrive\Desktop\HTML-CSS BEG\images\sk.webp")
img = Image.blend(img1,img2,alpha=0.5)
img.show()