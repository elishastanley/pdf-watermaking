import fitz  # PyMuPDF for PDF processing
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile
import os
import logging
import time
import argparse
import json
import sys
import psutil
import cProfile
import pstats

# Configure logging to write to both stderr and a log file
def setup_logging(log_file='watermark_log.log'):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # StreamHandler for stderr
    sh = logging.StreamHandler(sys.stderr)
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    # FileHandler for logging to a file
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

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

def get_system_resources():
    """
    Retrieves current system CPU and memory usage.
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    return cpu_percent, memory_percent

def adjust_workers(desired_workers, cpu_threshold=80, memory_threshold=80):
    """
    Adjusts the number of worker threads based on system resource usage.

    Args:
        desired_workers (int): Current number of worker threads.
        cpu_threshold (int): CPU usage percentage threshold.
        memory_threshold (int): Memory usage percentage threshold.

    Returns:
        int: Adjusted number of worker threads.
    """
    cpu, memory = get_system_resources()
    if cpu > cpu_threshold or memory > memory_threshold:
        # Reduce the number of workers to prevent system overload
        return max(1, desired_workers - 1)
    else:
        # Increase the number of workers if resources are available
        return desired_workers + 1

def watermark_pdf(input_pdf_path, output_pdf_path, watermark_image_path, opacity=0.2, max_workers=4, cpu_threshold=80, memory_threshold=80):
    """
    Watermarks all pages of a PDF with a transparent image under the content in parallel.
    Includes resource monitoring to adjust worker threads dynamically.

    Args:
        input_pdf_path (str): Path to the input PDF file.
        output_pdf_path (str): Path to save the watermarked PDF.
        watermark_image_path (str): Path to the watermark image file.
        opacity (float): Opacity level for the watermark.
        max_workers (int): Maximum number of threads for parallel processing.
        cpu_threshold (int): CPU usage percentage threshold to adjust workers.
        memory_threshold (int): Memory usage percentage threshold to adjust workers.
    """
    logging.info("Starting the watermarking process...")
    start_time = time.time()
    timing_data = {}
    try:
        # Prepare the watermark image
        processed_watermark = prepare_watermark(watermark_image_path, opacity)
        watermark_preparation_time = time.time()
        preparation_duration = watermark_preparation_time - start_time
        logging.info(f"Watermark preparation took {preparation_duration:.2f} seconds.")
        timing_data['watermark_preparation'] = preparation_duration

        with fitz.open(input_pdf_path) as pdf:
            total_pages = pdf.page_count
            logging.info(f"PDF opened. Total pages: {total_pages}")

            # Initialize ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit watermarking tasks for each page
                future_to_page = {
                    executor.submit(watermark_page_under, page, processed_watermark): page.number
                    for page in pdf
                }

                watermarked_pages = 0
                watermarking_start_time = time.time()
                for future in as_completed(future_to_page):
                    page_number = future_to_page[future]
                    try:
                        future.result()
                        watermarked_pages += 1
                        logging.info(f"Watermarked page {page_number + 1}/{total_pages}")
                        
                        # Periodically check system resources and adjust workers
                        if watermarked_pages % 50 == 0:  # Adjust every 50 pages
                            current_workers = executor._max_workers
                            adjusted_workers = adjust_workers(current_workers, cpu_threshold, memory_threshold)
                            if adjusted_workers != current_workers:
                                logging.info(f"Adjusting workers from {current_workers} to {adjusted_workers} based on system resources.")
                                executor._max_workers = adjusted_workers
                    except Exception as exc:
                        logging.error(f"Page {page_number + 1} generated an exception: {exc}")

                watermarking_end_time = time.time()
                watermarking_duration = watermarking_end_time - watermarking_start_time
                timing_data['watermarking'] = watermarking_duration

            # Save the watermarked PDF
            pdf.save(output_pdf_path)
            logging.info(f"Watermarked PDF saved as {output_pdf_path}")

        # Calculate and log saving duration
        watermark_post_process_time = time.time()
        saving_duration = watermark_post_process_time - watermark_preparation_time
        logging.info(f"Watermarking and saving took {saving_duration:.2f} seconds.")
        timing_data['watermarking_and_saving'] = saving_duration

        # Total process time
        total_time = watermark_post_process_time - start_time
        logging.info(f"Total watermarking process took {total_time:.2f} seconds.")
        timing_data['total_time'] = total_time

        # Output timing data as JSON to stdout
        print(json.dumps(timing_data))

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
    parser = argparse.ArgumentParser(description="Watermark all pages of a PDF with a transparent image.")
    parser.add_argument("input_pdf", help="Path to the input PDF file.")
    parser.add_argument("output_pdf", help="Path to save the watermarked PDF.")
    parser.add_argument("watermark_image", help="Path to the watermark image file.")
    parser.add_argument("--opacity", type=float, default=0.2, help="Opacity level for the watermark (0 to 1).")
    parser.add_argument("--workers", type=int, default=4, help="Number of parallel threads.")
    parser.add_argument("--profile", action='store_true', help="Enable profiling.")
    parser.add_argument("--profile_output", type=str, default="profile_output.prof", help="Path to save profiling data.")
    args = parser.parse_args()

    # Setup logging
    setup_logging()

    if args.profile:
        pr = cProfile.Profile()
        pr.enable()

    watermark_pdf(
        input_pdf_path=args.input_pdf,
        output_pdf_path=args.output_pdf,
        watermark_image_path=args.watermark_image,
        opacity=args.opacity,
        max_workers=args.workers
    )

    if args.profile:
        pr.disable()
        pr.dump_stats(args.profile_output)
        logging.info(f"Profiling data saved to {args.profile_output}")

if __name__ == "__main__":
    main()