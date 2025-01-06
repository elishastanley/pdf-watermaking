import fitz  # PyMuPDF for PDF processing
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

def prepare_watermark(watermark_image, opacity=0.2):
    """
    Reducing the opacity of the watermark image.
    Args:
        watermark_image: Path to the watermark image file.
        opacity: Opacity level (0 to 1).
    Returns:
        Path to the processed watermark image.
    """
    # Opening the watermark image and converting it to RGBA format
    img = Image.open(watermark_image).convert("RGBA")
    alpha = img.split()[3]  # Getting the alpha channel

    # Adjusting the alpha channel to apply the specified opacity
    alpha = alpha.point(lambda p: p * opacity)
    img.putalpha(alpha)

    # Saving the processed image to a temporary file
    processed_image = "processed_watermark.png"
    img.save(processed_image, "PNG")
    return processed_image

def watermark_page_under(pdf_page, watermark_image):
    """
    Applying a watermark image under the content of a single PDF page with a fixed size.
    Args:
        pdf_page: The PDF page object.
        watermark_image: Path to the watermark image.
    """
    # Getting the dimensions of the current PDF page
    rect = pdf_page.rect

    # Defining the watermark dimensions as one-third of the page dimensions
    watermark_width = rect.width / 3
    watermark_height = rect.height / 3

    # Calculating the position to center the watermark on the page
    x_center = (rect.width - watermark_width) / 2
    y_center = (rect.height - watermark_height) / 2

    # Creating a rectangle where the watermark will be placed
    watermark_rect = fitz.Rect(
        x_center, 
        y_center, 
        x_center + watermark_width, 
        y_center + watermark_height
    )

    # Inserting the watermark image under the content of the page
    pdf_page.insert_image(watermark_rect, filename=watermark_image, overlay=False)

def watermark_pdf(input_pdf, output_pdf, watermark_image):
    """
    Watermarking all pages of a PDF with a transparent image under the content in parallel.
    Args:
        input_pdf: Path to the input PDF file.
        output_pdf: Path to save the watermarked PDF.
        watermark_image: Path to the watermark image file.
    """
    # Preparing the watermark image by reducing its opacity
    processed_watermark = prepare_watermark(watermark_image, opacity=0.2)

    # Opening the input PDF file for reading
    pdf = fitz.open(input_pdf)

    # Using ThreadPoolExecutor to process pages in parallel
    with ThreadPoolExecutor() as executor:
        # Submitting watermarking tasks for all pages concurrently
        futures = [
            executor.submit(watermark_page_under, page, processed_watermark)
            for page in pdf
        ]

        # Waiting for all watermarking tasks to complete
        for future in futures:
            future.result()

    # Saving the watermarked PDF to the output file
    pdf.save(output_pdf)
    pdf.close()

if __name__ == "__main__":
    # Defining paths for the input PDF, output PDF, and watermark image
    input_pdf = "input.pdf"
    output_pdf = "output.pdf"
    watermark_image = "watermark.png"

    # Starting the watermarking process
    print("Watermarking process started...")
    watermark_pdf(input_pdf, output_pdf, watermark_image)
    print(f"Watermarked PDF saved as {output_pdf}")