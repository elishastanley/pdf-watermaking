import unittest
import subprocess
import os
import sys
import json
from PyPDF2 import PdfReader

class TestWatermarking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Set up paths and ensure output directory exists.
        """
        cls.parent_script = os.path.join(os.path.dirname(__file__), '..', 'parent_script.py')
        cls.input_dir = os.path.join(os.path.dirname(__file__), 'test_pdfs')
        cls.output_dir = os.path.join(os.path.dirname(__file__), 'output_pdfs')
        cls.watermark_image = os.path.join(os.path.dirname(__file__), '..', 'watermark.png')
        os.makedirs(cls.output_dir, exist_ok=True)

    def run_watermarking(self, input_pdf, output_pdf, opacity=0.2, workers=4, profile=False):
        """
        Runs the parent_script.py as a subprocess.
        """
        try:
            # Build the command
            cmd = [
                'python', self.parent_script,
                input_pdf,
                output_pdf,
                self.watermark_image,
                '--opacity', str(opacity),
                '--workers', str(workers)
            ]

            if profile:
                cmd.append('--profile')

            # Execute the subprocess
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.fail(f"Watermarking failed: {e.stderr}")

    def test_watermarking_small_pdf(self):
        input_pdf = os.path.join(self.input_dir, 'small.pdf')
        output_pdf = os.path.join(self.output_dir, 'small_watermarked.pdf')
        output = self.run_watermarking(input_pdf, output_pdf, opacity=0.3, workers=2)
        # Parse JSON timing data
        try:
            timing_data = json.loads(output.strip().split('\n')[-1])
            print(f"Timing for small.pdf: {timing_data}")
        except json.JSONDecodeError:
            self.fail("Failed to parse timing data.")

        # Verify that all pages are watermarked
        reader = PdfReader(output_pdf)
        self.assertEqual(len(reader.pages), 5)
        # Further verification can be added here, such as checking for watermark presence

    def test_watermarking_medium_pdf(self):
        input_pdf = os.path.join(self.input_dir, 'medium.pdf')
        output_pdf = os.path.join(self.output_dir, 'medium_watermarked.pdf')
        output = self.run_watermarking(input_pdf, output_pdf, opacity=0.3, workers=4)
        try:
            timing_data = json.loads(output.strip().split('\n')[-1])
            print(f"Timing for medium.pdf: {timing_data}")
        except json.JSONDecodeError:
            self.fail("Failed to parse timing data.")

        reader = PdfReader(output_pdf)
        self.assertEqual(len(reader.pages), 50)
        # Further verification can be added here

    def test_watermarking_large_pdf(self):
        input_pdf = os.path.join(self.input_dir, 'large.pdf')
        output_pdf = os.path.join(self.output_dir, 'large_watermarked.pdf')
        output = self.run_watermarking(input_pdf, output_pdf, opacity=0.3, workers=8)
        try:
            timing_data = json.loads(output.strip().split('\n')[-1])
            print(f"Timing for large.pdf: {timing_data}")
        except json.JSONDecodeError:
            self.fail("Failed to parse timing data.")

        reader = PdfReader(output_pdf)
        self.assertEqual(len(reader.pages), 200)
        # Further verification can be added here

if __name__ == '__main__':
    unittest.main()