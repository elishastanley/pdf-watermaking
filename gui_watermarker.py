import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import threading
import json
import os
import psutil
import sys

class WatermarkGUI:
    def __init__(self, master):
        self.master = master
        master.title("PDF Watermarking Tool")
        master.geometry("900x700")  # Increased window size for better layout
        master.resizable(False, False)

        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')  # 'clam' is more modern; adjust as needed

        # Create frames for better organization
        self.input_frame = ttk.LabelFrame(master, text="Input Files")
        self.input_frame.pack(fill="x", padx=20, pady=10)

        self.settings_frame = ttk.LabelFrame(master, text="Settings")
        self.settings_frame.pack(fill="x", padx=20, pady=10)

        self.progress_frame = ttk.LabelFrame(master, text="Progress")
        self.progress_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # -------------------------------
        # Input Frame Widgets
        # -------------------------------

        # Input PDF
        self.input_pdf_label = ttk.Label(self.input_frame, text="Input PDF:")
        self.input_pdf_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.input_pdf_entry = ttk.Entry(self.input_frame, width=60)
        self.input_pdf_entry.grid(row=0, column=1, padx=5, pady=5)
        self.input_pdf_button = ttk.Button(self.input_frame, text="Browse", command=self.browse_input_pdf)
        self.input_pdf_button.grid(row=0, column=2, padx=5, pady=5)

        # Watermark Image
        self.watermark_label = ttk.Label(self.input_frame, text="Watermark Image:")
        self.watermark_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.watermark_entry = ttk.Entry(self.input_frame, width=60)
        self.watermark_entry.grid(row=1, column=1, padx=5, pady=5)
        self.watermark_button = ttk.Button(self.input_frame, text="Browse", command=self.browse_watermark)
        self.watermark_button.grid(row=1, column=2, padx=5, pady=5)

        # Output PDF
        self.output_pdf_label = ttk.Label(self.input_frame, text="Output PDF:")
        self.output_pdf_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_pdf_entry = ttk.Entry(self.input_frame, width=60)
        self.output_pdf_entry.grid(row=2, column=1, padx=5, pady=5)
        self.output_pdf_button = ttk.Button(self.input_frame, text="Browse", command=self.browse_output_pdf)
        self.output_pdf_button.grid(row=2, column=2, padx=5, pady=5)

        # -------------------------------
        # Settings Frame Widgets
        # -------------------------------

        # Opacity
        self.opacity_label = ttk.Label(self.settings_frame, text="Opacity (0-1):")
        self.opacity_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=10)
        self.opacity_scale = ttk.Scale(self.settings_frame, from_=0, to=1, orient=tk.HORIZONTAL, value=0.2, command=self.update_opacity_label)
        self.opacity_scale.grid(row=0, column=1, padx=5, pady=10, sticky=tk.EW)
        self.opacity_value = ttk.Label(self.settings_frame, text="0.20")
        self.opacity_value.grid(row=0, column=2, sticky=tk.W, padx=5, pady=10)

        # Configure grid to make scale expand
        self.settings_frame.columnconfigure(1, weight=1)

        # Workers
        self.workers_label = ttk.Label(self.settings_frame, text="Workers:")
        self.workers_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=10)
        self.workers_spinbox = ttk.Spinbox(self.settings_frame, from_=1, to=32, width=5)
        self.workers_spinbox.set(4)
        self.workers_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5, pady=10)

        # Profile
        self.profile_var = tk.BooleanVar()
        self.profile_check = ttk.Checkbutton(self.settings_frame, text="Enable Profiling", variable=self.profile_var)
        self.profile_check.grid(row=2, column=1, sticky=tk.W, padx=5, pady=10)

        # -------------------------------
        # Progress Frame Widgets
        # -------------------------------

        # Overall Progress Bar
        self.progress_label = ttk.Label(self.progress_frame, text="Overall Progress:")
        self.progress_label.pack(anchor='w', padx=5, pady=5)
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", length=860, mode="determinate")
        self.progress_bar.pack(pady=5)

        # Resource Usage Frame
        self.resource_frame = ttk.Frame(self.progress_frame)
        self.resource_frame.pack(fill="x", pady=10)

        # CPU Usage
        self.cpu_label = ttk.Label(self.resource_frame, text="CPU Usage:")
        self.cpu_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.cpu_progress = ttk.Progressbar(self.resource_frame, orient="horizontal", length=200, mode="determinate")
        self.cpu_progress.grid(row=0, column=1, padx=5, pady=5)
        self.cpu_percent_label = ttk.Label(self.resource_frame, text="0%")
        self.cpu_percent_label.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)

        # Memory Usage
        self.memory_label = ttk.Label(self.resource_frame, text="Memory Usage:")
        self.memory_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.memory_progress = ttk.Progressbar(self.resource_frame, orient="horizontal", length=200, mode="determinate")
        self.memory_progress.grid(row=1, column=1, padx=5, pady=5)
        self.memory_percent_label = ttk.Label(self.resource_frame, text="0%")
        self.memory_percent_label.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)

        # Configure grid for resource_frame
        self.resource_frame.columnconfigure(1, weight=1)

        # Log Text with Scrollbar
        self.log_label = ttk.Label(self.progress_frame, text="Logs:")
        self.log_label.pack(anchor='w', padx=5, pady=(10, 0))
        self.log_text = tk.Text(self.progress_frame, height=20, width=110, state='disabled', wrap='word', bg="#f0f0f0")
        self.log_text.pack(fill="both", expand=True, pady=5)
        self.scrollbar = ttk.Scrollbar(self.progress_frame, orient='vertical', command=self.log_text.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.log_text['yscrollcommand'] = self.scrollbar.set

        # Define tags for colored logs
        self.log_text.tag_configure("INFO", foreground="green")
        self.log_text.tag_configure("ERROR", foreground="red")
        self.log_text.tag_configure("DEFAULT", foreground="black")

        # Initialize variables
        self.process = None
        self.stop_event = threading.Event()

        # Start resource monitoring
        self.update_resource_usage()

    def browse_input_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.input_pdf_entry.delete(0, tk.END)
            self.input_pdf_entry.insert(0, file_path)

    def browse_watermark(self):
        # Corrected filetypes with space-separated extensions
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if file_path:
            self.watermark_entry.delete(0, tk.END)
            self.watermark_entry.insert(0, file_path)

    def browse_output_pdf(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.output_pdf_entry.delete(0, tk.END)
            self.output_pdf_entry.insert(0, file_path)

    def update_opacity_label(self, event):
        value = self.opacity_scale.get()
        self.opacity_value.config(text=f"{value:.2f}")

    def start_watermarking(self):
        input_pdf = self.input_pdf_entry.get()
        output_pdf = self.output_pdf_entry.get()
        watermark_image = self.watermark_entry.get()
        opacity = self.opacity_scale.get()
        workers = self.workers_spinbox.get()
        profile = self.profile_var.get()

        if not all([input_pdf, output_pdf, watermark_image]):
            messagebox.showerror("Error", "Please select all required files.")
            return

        # Disable the start button to prevent multiple runs
        self.start_button.config(state='disabled')
        self.log_message("Starting watermarking process...\n", level="INFO")

        # Reset progress bar
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = 100  # Will be updated based on total pages

        # Run the watermarking in a separate thread to keep the GUI responsive
        threading.Thread(target=self.run_watermarking, args=(input_pdf, output_pdf, watermark_image, opacity, workers, profile), daemon=True).start()

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
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Read stdout in real-time
            for line in self.process.stdout:
                self.log_message(line)
                self.update_progress(line)

            # Read any remaining stderr
            stderr = self.process.stderr.read()
            if stderr:
                self.log_message(f"Error: {stderr}\n", level="ERROR")

            # Wait for the subprocess to finish
            self.process.wait()

            # Re-enable the start button
            self.start_button.config(state='normal')

            # Check return code
            if self.process.returncode == 0:
                self.log_message("Watermarking completed successfully.\n", level="INFO")
            else:
                self.log_message("Watermarking encountered errors.\n", level="ERROR")

        except Exception as e:
            self.log_message(f"An error occurred: {e}\n", level="ERROR")
            self.start_button.config(state='normal')

    def log_message(self, message, level="DEFAULT"):
        """
        Logs a message to the log_text widget with color based on the log level.
        """
        self.log_text.config(state='normal')
        if level == "INFO":
            tag = "INFO"
        elif level == "ERROR":
            tag = "ERROR"
        else:
            tag = "DEFAULT"

        # Insert the message with the appropriate tag
        self.log_text.insert(tk.END, message, tag)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def update_progress(self, message):
        """
        Updates the progress bar based on the number of pages processed.
        Expects messages like "Watermarked page X/Y"
        """
        if "Watermarked page" in message:
            try:
                parts = message.strip().split(' ')
                page_info = parts[-1]  # "X/Y"
                x, y = page_info.split('/')
                x = int(x)
                y = int(y)
                progress = (x / y) * 100
                self.progress_bar['value'] = progress
            except Exception:
                pass  # Ignore parsing errors

    def update_resource_usage(self):
        """
        Updates the CPU and Memory usage bars every second.
        """
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        # Update CPU Progress Bar
        self.cpu_progress['value'] = cpu_percent
        self.cpu_percent_label.config(text=f"{cpu_percent}%")

        # Update Memory Progress Bar
        self.memory_progress['value'] = memory_percent
        self.memory_percent_label.config(text=f"{memory_percent}%")

        # Schedule the next update
        self.master.after(1000, self.update_resource_usage)

    def on_closing(self):
        """
        Handles the window closing event.
        """
        if self.process and self.process.poll() is None:
            if messagebox.askokcancel("Quit", "Watermarking is still in progress. Do you want to quit?"):
                self.process.terminate()
                self.master.destroy()
        else:
            self.master.destroy()

def main():
    root = tk.Tk()
    gui = WatermarkGUI(root)

    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", gui.on_closing)

    root.mainloop()

if __name__ == "__main__":
    main()