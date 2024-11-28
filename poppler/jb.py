import time
from pdf2image import convert_from_path
from joblib import Parallel, delayed

def convert_pdf_page_to_image(pdf_path, page_number, dpi=300, poppler_path=None):
    try:
        images = convert_from_path(
            pdf_path, dpi=dpi, first_page=page_number, last_page=page_number, poppler_path=poppler_path
        )
        if not images:
            raise ValueError(f"Page {page_number} could not be converted.")
        return images[0]
    except Exception as e:
        print(f"Error converting page {page_number}: {e}")
        return None

def save_image(img, output_file):
    try:
        img.save(output_file, format="PNG")
        return f"Saved {output_file}"
    except Exception as e:
        print(f"Error saving {output_file}: {e}")
        return None

def process_page(pdf_path, page_number, dpi=300, poppler_path=None):
    img = convert_pdf_page_to_image(pdf_path, page_number, dpi, poppler_path)
    if img is not None:
        output_file = f"page_{page_number}_processed.png"
        return save_image(img, output_file)
    return f"Failed to process page {page_number}"

if __name__ == "__main__":
    starttime = time.time()
    pdf_path = r"C:\Users\MuraliDharan S\OneDrive\Desktop\Iterations-codility.pdf"
    total_pages = 4
    poppler_path = r"D:\Program Files\poppler-24.08.0\Library\bin"

    results = Parallel(n_jobs=-1)(delayed(process_page)(pdf_path, page_number, 300, poppler_path) for page_number in range(1, total_pages + 1))

    print("\n".join(results))
    endtime = time.time()
    print(f"\nTotal execution time (using Joblib): {endtime - starttime:.2f} seconds")
