from PIL import Image
img = Image.open(r"C:\Users\MuraliDharan S\OneDrive\Desktop\HTML-CSS BEG\images\shinchan.jpg")
img = img.rotate(angle=90,expand=True,fillcolor='white')
img .show()