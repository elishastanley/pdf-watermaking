# PDF Watermarking Tool

![PDF Watermarking](https://img.shields.io/badge/PDF-Watermarking-blue)
![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
  - [Command-Line Interface (CLI)](#command-line-interface-cli)
  - [Graphical User Interface (GUI)](#graphical-user-interface-gui)
- [Automated Testing](#automated-testing)
- [Profiling](#profiling)
- [Logging](#logging)
- [Resource Management](#resource-management)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The **PDF Watermarking Tool** is a versatile Python application designed to batch watermark PDF documents efficiently. Whether you're a professional securing documents or an individual personalizing PDFs, this tool offers a user-friendly interface and robust functionalities to meet your needs.

## Features

- Batch watermarking for PDFs.
- Customizable watermark opacity.
- Multi-threaded for faster processing.
- Real-time CPU and memory monitoring in the GUI.
- Detailed logs for transparency and troubleshooting.
- Automated testing to ensure reliability.
- Profiling tools to optimize performance.
- CLI and GUI interfaces.

## Project Structure

```plaintext
pdf_watermarker/
├── watermark_pdf.py         # Core watermarking script
├── parent_script.py         # Manages subprocesses and profiling
├── gui_watermarker.py       # Enhanced GUI built with Tkinter
├── tests/
│   ├── test_watermarking.py # Automated testing script
│   ├── generate_pdfs.py     # Script to generate test PDFs
│   └── test_pdfs/           # Folder for test PDFs
├── input.pdf                # Example input PDF (optional)
├── watermark.png            # Example watermark image
├── watermark_log.log        # Log file for the application
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

## Installation

### Prerequisites

- **Python 3.7+**
- **pip** (Python package manager)

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/elisha/pdf_watermarker.git
   cd pdf_watermarker
   ```

2. **Create a virtual environment (optional)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Command-Line Interface (CLI)

1. **Basic command**:
   ```bash
   python parent_script.py input.pdf output.pdf watermark.png
   ```
   - Replace `input.pdf`, `output.pdf`, and `watermark.png` with your file paths.

2. **With advanced options**:
   - Set watermark opacity:
     ```bash
     python parent_script.py input.pdf output.pdf watermark.png --opacity 0.5
     ```
   - Set the number of worker threads:
     ```bash
     python parent_script.py input.pdf output.pdf watermark.png --workers 8
     ```
   - Enable profiling:
     ```bash
     python parent_script.py input.pdf output.pdf watermark.png --profile
     ```

---

### Graphical User Interface (GUI)

1. **Launch the GUI**:
   ```bash
   python gui_watermarker.py
   ```

2. **Using the GUI**:
   - **Select Files**:
     - Input PDF: Click "Browse" to select the PDF.
     - Watermark Image: Click "Browse" to select the watermark image.
     - Output PDF: Specify where to save the watermarked PDF.
   - **Adjust Settings**:
     - Set watermark opacity using the slider.
     - Choose the number of worker threads.
     - Enable profiling if desired.
   - **Start Watermarking**:
     - Click the "Start Watermarking" button.
     - Monitor progress, CPU/memory usage, and logs in real-time.

---

## Automated Testing

### Generate Test PDFs
1. Run the test PDF generation script:
   ```bash
   cd tests
   python generate_pdfs.py
   cd ..
   ```

2. Run the tests:
   ```bash
   python -m unittest discover tests
   ```

---

## Profiling

### Enable Profiling

Run the watermarking process with profiling:
```bash
python parent_script.py input.pdf output.pdf watermark.png --profile
```

### Visualize with `snakeviz`
1. Install `snakeviz`:
   ```bash
   pip install snakeviz
   ```
2. View profiling data:
   ```bash
   snakeviz profile_output.prof
   ```

---

## Logging

Logs are saved to `watermark_log.log` and displayed in the console/GUI. Example:
```plaintext
2025-01-06 10:00:00 - INFO - Starting watermarking...
2025-01-06 10:00:01 - INFO - Processed watermark saved.
2025-01-06 10:10:00 - INFO - Watermarking completed.
```

---

## Resource Management

- Monitors system resources (CPU, memory).
- Dynamically adjusts worker threads based on system load.

---

## Contributing

1. **Fork the repository**.
2. **Create a feature branch**:
   ```bash
   git checkout -b feature-name
   ```
3. **Commit your changes**:
   ```bash
   git commit -m "Added feature"
   ```
4. **Push to your fork**:
   ```bash
   git push origin feature-name
   ```
5. **Submit a pull request**.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

**Happy Watermarking!** If you encounter any issues, feel free to open an issue or contribute.

---