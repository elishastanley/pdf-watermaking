import subprocess
import sys

def watermark_pdf(input_pdf, output_pdf, watermark_image, opacity=0.2, workers=4):
    """
    Calls the watermark_pdf.py script as a subprocess.
    """
    try:
        result = subprocess.run([
            'python', 'watermark_pdf.py',
            input_pdf,
            output_pdf,
            watermark_image,
            '--opacity', str(opacity),
            '--workers', str(workers)
        ], check=True, capture_output=True, text=True)
        print("Watermarking completed successfully.")
        print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error during watermarking:", e.stderr, file=sys.stderr)

if __name__ == "__main__":
    watermark_pdf('input.pdf', 'output.pdf', 'watermark.png', opacity=0.3, workers=8)