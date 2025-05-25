#!/usr/bin/env python3
"""
Usage example for the PDF to Speech converter
"""

import subprocess
import sys
import os

def main():
    # Check if example PDF exists
    example_pdf = "examples/SexualPowerDynamicsinABBAsWaterlooALyricAnalysis.pdf"
    
    if not os.path.exists(example_pdf):
        print(f"Example PDF not found: {example_pdf}")
        print("Please provide a PDF path as an argument:")
        print("python pdf_to_speech.py /path/to/your/file.pdf")
        return
    
    print(f"Testing with example PDF: {example_pdf}")
    print("Make sure you have set your OPENAI_API_KEY environment variable")
    print()
    
    # Run the PDF to speech converter
    try:
        subprocess.run([sys.executable, "pdf_to_speech.py", example_pdf], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running pdf_to_speech.py: {e}")
    except KeyboardInterrupt:
        print("\nInterrupted by user")

if __name__ == "__main__":
    main()