import subprocess
import sys
import time
import json
import argparse
import os

def watermark_pdf(input_pdf, output_pdf, watermark_image, opacity=0.2, workers=4, profile=False):
    """
    Calls the watermark_pdf.py script as a subprocess, measures execution time, and parses timing data.
    """
    try:
        # Recording the start time from the parent script's perspective
        parent_start_time = time.time()

        # Building the command
        cmd = [
            'python', 'watermark_pdf.py',
            input_pdf,
            output_pdf,
            watermark_image,
            '--opacity', str(opacity),
            '--workers', str(workers)
        ]

        if profile:
            cmd.extend(['--profile', '--profile_output', 'profile_output.prof'])

        # Executing the watermark_pdf.py script as a subprocess
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )

        # Recording the end time after subprocess completion
        parent_end_time = time.time()

        # Capturing the JSON timing data from stdout
        # Assuming JSON is printed at the end, find the last JSON object
        stdout = result.stdout.strip()
        json_output = None
        for line in reversed(stdout.split('\n')):
            try:
                json_output = json.loads(line)
                break
            except json.JSONDecodeError:
                continue

        if json_output:
            print("Watermarking completed successfully.")
            print("Timing data from watermark_pdf.py:")
            print(json.dumps(json_output, indent=4))
        else:
            print("Watermarking completed successfully, but failed to parse timing data.")

        if profile:
            # Assuming profiling data is saved to a file
            print("\nProfiling data saved to profile_output.prof.")

        # Calculating and print the total execution time from the parent script's perspective
        parent_total_time = parent_end_time - parent_start_time
        print(f"\nTotal execution time from parent script: {parent_total_time:.2f} seconds.")

    except subprocess.CalledProcessError as e:
        print("Error during watermarking:", e.stderr, file=sys.stderr)
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}", file=sys.stderr)

def main():
    """
    Main function to parse command-line arguments and execute watermarking.
    """
    parser = argparse.ArgumentParser(description="Automate the PDF watermarking process.")
    parser.add_argument("input_pdf", help="Path to the input PDF file.")
    parser.add_argument("output_pdf", help="Path to save the watermarked PDF.")
    parser.add_argument("watermark_image", help="Path to the watermark image file.")
    parser.add_argument("--opacity", type=float, default=0.2, help="Opacity level for the watermark (0 to 1). Default is 0.2.")
    parser.add_argument("--workers", type=int, default=4, help="Number of parallel threads. Default is 4.")
    parser.add_argument("--profile", action='store_true', help="Enable profiling to identify performance bottlenecks.")
    args = parser.parse_args()

    watermark_pdf(
        input_pdf=args.input_pdf,
        output_pdf=args.output_pdf,
        watermark_image=args.watermark_image,
        opacity=args.opacity,
        workers=args.workers,
        profile=args.profile
    )

if __name__ == "__main__":
    main()