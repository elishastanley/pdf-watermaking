import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import json
import os

class WatermarkGUI:
    def __init__(self, master):
        self.master = master
        master.title("PDF Watermarking Tool")

        # Input PDF
        self.input_pdf_label = tk.Label(master, text="Input PDF:")
        self.input_pdf_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.input_pdf_entry = tk.Entry(master, width=50)
        self.input_pdf_entry.grid(row=0, column=1, padx=5, pady=5)
        self.input_pdf_button = tk.Button(master, text="Browse", command=self.browse_input_pdf)
        self.input_pdf_button.grid(row=0, column=2, padx=5, pady=5)

        # Watermark Image
        self.watermark_label = tk.Label(master, text="Watermark Image:")
        self.watermark_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.watermark_entry = tk.Entry(master, width=50)
        self.watermark_entry.grid(row=1, column=1, padx=5, pady=5)
        self.watermark_button = tk.Button(master, text="Browse", command=self.browse_watermark)
        self.watermark_button.grid(row=1, column=2, padx=5, pady=5)

        # Output PDF
        self.output_pdf_label = tk.Label(master, text="Output PDF:")
        self.output_pdf_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_pdf_entry = tk.Entry(master, width=50)
        self.output_pdf_entry.grid(row=2, column=1, padx=5, pady=5)
        self.output_pdf_button = tk.Button(master, text="Browse", command=self.browse_output_pdf)
        self.output_pdf_button.grid(row=2, column=2, padx=5, pady=5)

        # Opacity
        self.opacity_label = tk.Label(master, text="Opacity (0-1):")
        self.opacity_label.grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.opacity_scale = tk.Scale(master, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL)
        self.opacity_scale.set(0.2)
        self.opacity_scale.grid(row=3, column=1, padx=5, pady=5)

        # Workers
        self.workers_label = tk.Label(master, text="Workers:")
        self.workers_label.grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.workers_spinbox = tk.Spinbox(master, from_=1, to=32, width=5)
        self.workers_spinbox.delete(0, tk.END)
        self.workers_spinbox.insert(0, "4")
        self.workers_spinbox.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)

        # Profile
        self.profile_var = tk.IntVar()
        self.profile_check = tk.Checkbutton(master, text="Enable Profiling", variable=self.profile_var)
        self.profile_check.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)

        # Start Button
        self.start_button = tk.Button(master, text="Start Watermarking", command=self.start_watermarking)
        self.start_button.grid(row=6, column=1, pady=10)

        # Progress Text
        self.progress_text = tk.Text(master, height=15, width=80, state='disabled')
        self.progress_text.grid(row=7, column=0, columnspan=3, padx=5, pady=5)

    def browse_input_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.input_pdf_entry.delete(0, tk.END)
            self.input_pdf_entry.insert(0, file_path)

    def browse_watermark(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.watermark_entry.delete(0, tk.END)
            self.watermark_entry.insert(0, file_path)

    def browse_output_pdf(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.output_pdf_entry.delete(0, tk.END)
            self.output_pdf_entry.insert(0, file_path)

    def start_watermarking(self):
        input_pdf = self.input_pdf_entry.get()
        output_pdf = self.output_pdf_entry.get()
        watermark_image = self.watermark_entry.get()
        opacity = self.opacity_scale.get()
        workers = self.workers_spinbox.get()
        profile = bool(self.profile_var.get())

        if not all([input_pdf, output_pdf, watermark_image]):
            messagebox.showerror("Error", "Please select all required files.")
            return

        # Disable the start button to prevent multiple runs
        self.start_button.config(state='disabled')
        self.log_message("Starting watermarking process...\n")

        # Run the watermarking in a separate thread to keep the GUI responsive
        threading.Thread(target=self.run_watermarking, args=(input_pdf, output_pdf, watermark_image, opacity, workers, profile)).start()

    def run_watermarking(self, input_pdf, output_pdf, watermark_image, opacity, workers, profile):
        try:
            # Build the command
            cmd = [
                'python', 'parent_script.py',
                input_pdf,
                output_pdf,
                watermark_image,
                '--opacity', str(opacity),
                '--workers', str(workers)
            ]

            if profile:
                cmd.append('--profile')

            # Execute the subprocess
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Capture and display output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_message(output)

            # Capture any remaining stderr
            stderr = process.stderr.read()
            if stderr:
                self.log_message(f"Error: {stderr}\n")

            # Check return code
            if process.returncode == 0:
                self.log_message("Watermarking completed successfully.\n")
            else:
                self.log_message("Watermarking encountered errors.\n")

        except Exception as e:
            self.log_message(f"An error occurred: {e}\n")
        finally:
            # Re-enable the start button
            self.start_button.config(state='normal')

    def log_message(self, message):
        self.progress_text.config(state='normal')
        self.progress_text.insert(tk.END, message)
        self.progress_text.see(tk.END)
        self.progress_text.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    gui = WatermarkGUI(root)
    root.mainloop()