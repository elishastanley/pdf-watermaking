import fitz  # PyMuPDF for PDF processing
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile
import os
import logging

# Configure logging for better traceability and debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def prepare_watermark(watermark_image_path, opacity=0.2):
    """
    Reduces the opacity of the watermark image and saves it as a temporary file.

    Args:
        watermark_image_path (str): Path to the watermark image file.
        opacity (float): Opacity level (0 to 1).

    Returns:
        str: Path to the processed temporary watermark image.
    """
    try:
        with Image.open(watermark_image_path).convert("RGBA") as img:
            alpha = img.split()[3]
            alpha = alpha.point(lambda p: int(p * opacity))
            img.putalpha(alpha)

            temp_dir = tempfile.gettempdir()
            processed_image_path = os.path.join(temp_dir, "processed_watermark.png")
            img.save(processed_image_path, "PNG")
            logging.info(f"Processed watermark saved at {processed_image_path}")
            return processed_image_path
    except Exception as e:
        logging.error(f"Error processing watermark image: {e}")
        raise

def watermark_page_under(pdf_page, watermark_image_path):
    """
    Applies a watermark image under the content of a single PDF page.

    Args:
        pdf_page (fitz.Page): The PDF page object.
        watermark_image_path (str): Path to the processed watermark image.
    """
    try:
        rect = pdf_page.rect
        watermark_width = rect.width / 3
        watermark_height = rect.height / 3
        x_center = (rect.width - watermark_width) / 2
        y_center = (rect.height - watermark_height) / 2
        watermark_rect = fitz.Rect(
            x_center, 
            y_center, 
            x_center + watermark_width, 
            y_center + watermark_height
        )
        pdf_page.insert_image(watermark_rect, filename=watermark_image_path, overlay=False)
        logging.debug(f"Watermark applied to page {pdf_page.number + 1}")
    except Exception as e:
        logging.error(f"Error watermarking page {pdf_page.number + 1}: {e}")
        raise

def watermark_pdf(input_pdf_path, output_pdf_path, watermark_image_path, opacity=0.2, max_workers=4):
    """
    Watermarks all pages of a PDF with a transparent image under the content in parallel.

    Args:
        input_pdf_path (str): Path to the input PDF file.
        output_pdf_path (str): Path to save the watermarked PDF.
        watermark_image_path (str): Path to the watermark image file.
        opacity (float): Opacity level for the watermark.
        max_workers (int): Maximum number of threads for parallel processing.
    """
    logging.info("Starting the watermarking process...")
    try:
        processed_watermark = prepare_watermark(watermark_image_path, opacity)

        with fitz.open(input_pdf_path) as pdf:
            total_pages = pdf.page_count
            logging.info(f"PDF opened. Total pages: {total_pages}")

            # Using ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Dictionary to keep track of futures
                future_to_page = {
                    executor.submit(watermark_page_under, page, processed_watermark): page.number
                    for page in pdf
                }

                for future in as_completed(future_to_page):
                    page_number = future_to_page[future]
                    try:
                        future.result()
                        logging.info(f"Watermarked page {page_number + 1}/{total_pages}")
                    except Exception as exc:
                        logging.error(f"Page {page_number + 1} generated an exception: {exc}")

            pdf.save(output_pdf_path)
            logging.info(f"Watermarked PDF saved as {output_pdf_path}")

        # Clean up the temporary watermark image
        if os.path.exists(processed_watermark):
            os.remove(processed_watermark)
            logging.debug(f"Temporary watermark image {processed_watermark} deleted.")

    except Exception as e:
        logging.error(f"Failed to watermark PDF: {e}")
        raise

def main():
    """
    Main function to execute the watermarking script.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Watermark all pages of a PDF with a transparent image.")
    parser.add_argument("input_pdf", help="Path to the input PDF file.")
    parser.add_argument("output_pdf", help="Path to save the watermarked PDF.")
    parser.add_argument("watermark_image", help="Path to the watermark image file.")
    parser.add_argument("--opacity", type=float, default=0.2, help="Opacity level for the watermark (0 to 1).")
    parser.add_argument("--workers", type=int, default=4, help="Number of parallel threads.")
    args = parser.parse_args()

    watermark_pdf(
        input_pdf_path=args.input_pdf,
        output_pdf_path=args.output_pdf,
        watermark_image_path=args.watermark_image,
        opacity=args.opacity,
        max_workers=args.workers
    )

if __name__ == "__main__":
    main()