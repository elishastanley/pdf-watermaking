import fitz  # PyMuPDF for PDF processing
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

def prepare_watermark(watermark_image, opacity=0.2):
    """
    Reduce the opacity of the watermark image.
    Args:
        watermark_image: Path to the watermark image file.
        opacity: Opacity level (0 to 1).
    Returns:
        Path to the processed watermark image.
    """
    # Open the image
    img = Image.open(watermark_image).convert("RGBA")
    alpha = img.split()[3]  # Get the alpha channel

    # Adjust the alpha channel for opacity
    alpha = alpha.point(lambda p: p * opacity)
    img.putalpha(alpha)

    # Save the processed image to a temporary file
    processed_image = "processed_watermark.png"
    img.save(processed_image, "PNG")
    return processed_image

def watermark_page_under(pdf_page, watermark_image):
    """
    Apply a watermark image under the content of a single PDF page with a fixed size.
    Args:
        pdf_page: The PDF page object.
        watermark_image: Path to the watermark image.
    """
    rect = pdf_page.rect  # Get the page dimensions

    # Define the desired width and height for the watermark (adjust as needed)
    watermark_width = rect.width / 3  # 1/3 of page width
    watermark_height = rect.height / 3  # 1/3 of page height

    # Calculate the position to center the watermark
    x_center = (rect.width - watermark_width) / 2
    y_center = (rect.height - watermark_height) / 2

    watermark_rect = fitz.Rect(
        x_center, 
        y_center, 
        x_center + watermark_width, 
        y_center + watermark_height
    )

    # Insert the watermark image
    pdf_page.insert_image(watermark_rect, filename=watermark_image, overlay=False)

def watermark_pdf(input_pdf, output_pdf, watermark_image):
    """
    Watermark all pages of a PDF with a transparent image under the content in parallel.
    Args:
        input_pdf: Path to the input PDF file.
        output_pdf: Path to save the watermarked PDF.
        watermark_image: Path to the watermark image file.
    """
    # Pre-process the watermark image for reduced opacity
    processed_watermark = prepare_watermark(watermark_image, opacity=0.2)

    # Open the input PDF
    pdf = fitz.open(input_pdf)

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor() as executor:
        # Submit watermark tasks for all pages simultaneously
        futures = [
            executor.submit(watermark_page_under, page, processed_watermark)
            for page in pdf
        ]

        # Wait for all watermarking tasks to complete
        for future in futures:
            future.result()

    # Save the modified PDF to the output file
    pdf.save(output_pdf)
    pdf.close()

if __name__ == "__main__":
    # Define input, output, and watermark file paths
    input_pdf = "input.pdf"
    output_pdf = "output.pdf"
    watermark_image = "watermark.png"

    print("Watermarking process started...")
    watermark_pdf(input_pdf, output_pdf, watermark_image)
    print(f"Watermarked PDF saved as {output_pdf}")