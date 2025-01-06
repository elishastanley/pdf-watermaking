from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import os

def create_pdf(file_path, num_pages):
    c = canvas.Canvas(file_path, pagesize=LETTER)
    width, height = LETTER
    for i in range(1, num_pages + 1):
        text = f"Page {i}"
        c.drawString(100, height - 100, text)
        c.showPage()
    c.save()

if __name__ == "__main__":
    os.makedirs('test_pdfs', exist_ok=True)
    sizes = {
        'small.pdf': 5,
        'medium.pdf': 50,
        'large.pdf': 200
    }
    for filename, pages in sizes.items():
        path = os.path.join('test_pdfs', filename)
        create_pdf(path, pages)
        print(f"Created {path} with {pages} pages.")