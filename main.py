#!/usr/bin/env python3
"""
PDF Speak Easy - A Mac app for reading PDFs aloud
"""

import sys
import os
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import PyPDF2
import pyttsx3
import wave
import tempfile
import json

class PDFSpeakEasy:
    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.title("PDF Speak Easy")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        
        # Initialize TTS engine
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        
        # State variables
        self.current_pdf_path = None
        self.extracted_text = ""
        self.audio_cache_path = None
        self.is_speaking = False
        
        self.setup_ui()
        self.setup_drag_drop()
        
        # Check if launched with PDF file argument
        if len(sys.argv) > 1 and sys.argv[1].endswith('.pdf'):
            self.process_pdf(sys.argv[1])
    
    def setup_tts(self):
        """Configure text-to-speech engine"""
        # Set voice to a pleasant one
        voices = self.tts_engine.getProperty('voices')
        # Try to find a female voice for more pleasant reading
        for voice in voices:
            if 'female' in voice.name.lower() or 'samantha' in voice.name.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        
        # Set speech rate (words per minute)
        self.tts_engine.setProperty('rate', 180)
        
        # Set volume
        self.tts_engine.setProperty('volume', 0.8)
    
    def setup_ui(self):
        """Create the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="PDF Speak Easy", 
                               font=('Helvetica', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Drop zone
        self.drop_frame = tk.Frame(main_frame, bg='lightblue', 
                                  relief='dashed', bd=2, height=100)
        self.drop_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), 
                            pady=(0, 20))
        self.drop_frame.grid_propagate(False)
        
        drop_label = tk.Label(self.drop_frame, text="Drop PDF here or click to select", 
                             bg='lightblue', font=('Helvetica', 12))
        drop_label.pack(expand=True)
        
        # Bind click to file selection
        self.drop_frame.bind("<Button-1>", self.select_file)
        drop_label.bind("<Button-1>", self.select_file)
        
        # File info
        self.file_label = ttk.Label(main_frame, text="No file selected")
        self.file_label.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), 
                            pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), 
                              pady=(5, 20))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
        button_frame.columnconfigure((0, 1, 2), weight=1)
        
        self.read_button = ttk.Button(button_frame, text="Read Aloud", 
                                     command=self.start_reading, state='disabled')
        self.read_button.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                     command=self.stop_reading, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        self.save_button = ttk.Button(button_frame, text="Save Audio", 
                                     command=self.save_audio, state='disabled')
        self.save_button.grid(row=0, column=2, padx=(5, 0), sticky=(tk.W, tk.E))
    
    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)
    
    def on_drop(self, event):
        """Handle file drop"""
        files = self.root.tk.splitlist(event.data)
        if files:
            file_path = files[0]
            if file_path.lower().endswith('.pdf'):
                self.process_pdf(file_path)
            else:
                messagebox.showerror("Error", "Please drop a PDF file")
    
    def select_file(self, event=None):
        """Open file dialog to select PDF"""
        file_path = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf")]
        )
        if file_path:
            self.process_pdf(file_path)
    
    def process_pdf(self, file_path):
        """Process PDF file in background thread"""
        self.current_pdf_path = file_path
        self.file_label.config(text=f"File: {os.path.basename(file_path)}")
        
        # Check for existing audio cache
        self.audio_cache_path = file_path + ".wav"
        if os.path.exists(self.audio_cache_path):
            self.progress_var.set("Found cached audio - ready to play!")
            self.read_button.config(state='normal')
            self.save_button.config(state='normal')
            return
        
        # Extract text in background
        threading.Thread(target=self.extract_text, daemon=True).start()
    
    def extract_text(self):
        """Extract text from PDF"""
        try:
            self.progress_var.set("Extracting text from PDF...")
            self.progress_bar.start()
            
            with open(self.current_pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_parts = []
                
                total_pages = len(pdf_reader.pages)
                for i, page in enumerate(pdf_reader.pages):
                    self.progress_var.set(f"Extracting text... Page {i+1}/{total_pages}")
                    text_parts.append(page.extract_text())
                
                self.extracted_text = ' '.join(text_parts)
            
            self.progress_bar.stop()
            
            if self.extracted_text.strip():
                self.progress_var.set("Text extracted - ready to read!")
                self.read_button.config(state='normal')
                # Start generating audio cache immediately
                threading.Thread(target=self.generate_audio_cache, daemon=True).start()
            else:
                self.progress_var.set("No text found in PDF")
                messagebox.showwarning("Warning", "No readable text found in the PDF")
                
        except Exception as e:
            self.progress_bar.stop()
            self.progress_var.set("Error extracting text")
            messagebox.showerror("Error", f"Failed to extract text: {str(e)}")
    
    def generate_audio_cache(self):
        """Generate audio file for caching"""
        try:
            self.progress_var.set("Generating audio cache...")
            self.progress_bar.start()
            
            # Save to temporary file first, then move to final location
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            
            self.tts_engine.save_to_file(self.extracted_text, temp_path)
            self.tts_engine.runAndWait()
            
            # Move to final location
            os.rename(temp_path, self.audio_cache_path)
            
            self.progress_bar.stop()
            self.progress_var.set("Audio cached - ready to play!")
            self.save_button.config(state='normal')
            
        except Exception as e:
            self.progress_bar.stop()
            self.progress_var.set("Error generating audio")
            print(f"Audio generation error: {e}")
    
    def start_reading(self):
        """Start reading the PDF aloud"""
        if not self.extracted_text:
            return
        
        self.is_speaking = True
        self.read_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress_var.set("Reading aloud...")
        
        # Use existing audio cache if available
        if os.path.exists(self.audio_cache_path):
            threading.Thread(target=self.play_cached_audio, daemon=True).start()
        else:
            # Stream TTS directly for immediate playback
            threading.Thread(target=self.stream_tts, daemon=True).start()
    
    def play_cached_audio(self):
        """Play the cached audio file"""
        try:
            # Use system audio player for better performance
            os.system(f'afplay "{self.audio_cache_path}"')
        except Exception as e:
            print(f"Error playing cached audio: {e}")
        finally:
            self.reading_finished()
    
    def stream_tts(self):
        """Stream TTS for immediate playback"""
        try:
            self.tts_engine.say(self.extracted_text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"TTS streaming error: {e}")
        finally:
            self.reading_finished()
    
    def stop_reading(self):
        """Stop reading"""
        self.is_speaking = False
        self.tts_engine.stop()
        
        # Stop any playing audio
        os.system('killall afplay 2>/dev/null')
        
        self.reading_finished()
    
    def reading_finished(self):
        """Called when reading is complete"""
        self.is_speaking = False
        self.read_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_var.set("Ready")
    
    def save_audio(self):
        """Save audio to custom location"""
        if not os.path.exists(self.audio_cache_path):
            messagebox.showwarning("Warning", "No audio file available to save")
            return
        
        save_path = filedialog.asksaveasfilename(
            title="Save audio file",
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
            initialname=os.path.basename(self.current_pdf_path) + ".wav"
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy2(self.audio_cache_path, save_path)
                messagebox.showinfo("Success", f"Audio saved to {save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save audio: {str(e)}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    app = PDFSpeakEasy()
    app.run()

if __name__ == "__main__":
    main()