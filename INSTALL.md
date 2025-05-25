# PDF Speak Easy Installation Guide

## Quick Install

1. **Clone and Build**:
   ```bash
   git clone https://github.com/your-username/pdf-speak-easy.git
   cd pdf-speak-easy
   chmod +x build_app.sh
   ./build_app.sh
   ```

2. **Install the App**:
   ```bash
   cd installer
   ./install.sh
   ```

## Manual Installation

### Prerequisites
- macOS 10.13 or later (Apple Silicon recommended)
- Python 3.8+ installed
- Xcode Command Line Tools: `xcode-select --install`

### Step-by-Step Installation

1. **Setup Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   ```

2. **Install Dependencies**:
   ```bash
   pip install PyPDF2 pyttsx3 tkinterdnd2
   pip install py2app  # For building the app
   ```

3. **Run the Application**:
   ```bash
   python main.py
   ```

4. **Build Mac App** (Optional):
   ```bash
   python setup.py py2app
   cp -R dist/main.app /Applications/PDF\ Speak\ Easy.app
   ```

5. **Install Context Menu** (Optional):
   ```bash
   python install_context_menu.py
   ```

## Features

✅ **Drag & Drop PDF Support** - Simply drag PDF files into the app window  
✅ **Streaming Text-to-Speech** - Start speaking immediately while processing  
✅ **Audio Caching** - Automatically saves `.pdf.wav` files for quick replay  
✅ **Progress Indicators** - Visual feedback during text extraction and audio generation  
✅ **Right-Click Integration** - Context menu option for PDF files in Finder  
✅ **Apple Silicon Optimized** - Native performance on M1/M2 Macs  

## Usage

### Basic Usage
1. Launch "PDF Speak Easy" from Applications
2. Drag a PDF file into the blue drop zone, or click to select a file
3. The app will extract text and begin reading immediately
4. Audio files are automatically cached next to the original PDF

### Right-Click Integration
After installation, you can right-click any PDF file in Finder and select "Read PDF Aloud" to launch the app with that file.

### Audio Cache
- Audio files are saved as `filename.pdf.wav` next to the original PDF
- Cached audio provides instant playback on subsequent runs
- You can copy/move these audio files independently

## Supported Formats

- **Input**: PDF files (text-based, not scanned images)
- **Output**: WAV audio files
- **Text-to-Speech**: Uses macOS built-in high-quality voices

## Troubleshooting

### App Won't Launch
- Ensure Python 3.8+ is installed
- Try running from Terminal: `python main.py`
- Check that all dependencies are installed

### No Audio Output
- Check system audio settings
- Ensure volume is turned up
- Try a different PDF file (some PDFs may have no extractable text)

### Context Menu Not Appearing
- Run the installer again: `python install_context_menu.py`
- Restart Finder: `killall Finder`
- Log out and back in

### Permission Issues
- Grant microphone access if prompted (for some TTS engines)
- Ensure the app has permission to access files

## Technical Details

- **GUI Framework**: Tkinter with drag-and-drop support
- **PDF Processing**: PyPDF2 for text extraction
- **Text-to-Speech**: pyttsx3 with macOS System voices
- **Audio Format**: WAV (uncompressed, high quality)
- **Caching**: Automatic WAV file generation next to source PDF

## Uninstallation

To remove PDF Speak Easy:
1. Delete `/Applications/PDF Speak Easy.app`
2. Remove the service: `rm -rf ~/Library/Services/Read\ PDF\ Aloud.workflow`
3. Restart Finder: `killall Finder`

## Building from Source

The app can be built as a standalone macOS application bundle:

```bash
# Install py2app
pip install py2app

# Build the app
python setup.py py2app

# The built app will be in dist/main.app
```

## Customization

### Voice Settings
Edit `main.py` and modify the `setup_tts()` function to change:
- Voice selection (male/female/accent)
- Speaking rate (words per minute)
- Volume level

### Audio Format
To change from WAV to another format, modify the audio file extension in the `generate_audio_cache()` function.