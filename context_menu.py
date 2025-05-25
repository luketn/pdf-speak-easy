#!/usr/bin/env python3
"""
Context menu script for PDF Speak Easy
This script is called when right-clicking on a PDF file
"""

import sys
import subprocess
import os

def main():
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        app_path = os.path.join(os.path.dirname(__file__), 'main.py')
        
        # Launch the main app with the PDF file
        subprocess.Popen([sys.executable, app_path, pdf_path])

if __name__ == "__main__":
    main()