#!/bin/bash

# Build script for PDF Speak Easy Mac app

echo "Building PDF Speak Easy..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install py2app

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build the app
echo "Building macOS app..."
python setup.py py2app

# Create installer directory structure
echo "Creating installer package..."
mkdir -p installer/PDF\ Speak\ Easy.app
cp -R dist/main.app/* installer/PDF\ Speak\ Easy.app/

# Create a simple installer script
cat > installer/install.sh << 'EOF'
#!/bin/bash
echo "Installing PDF Speak Easy..."
cp -R "PDF Speak Easy.app" /Applications/
echo "Installing context menu service..."
cd "PDF Speak Easy.app/Contents/Resources/"
python3 install_context_menu.py
echo "Installation complete! PDF Speak Easy is now available in your Applications folder."
echo "Right-click on any PDF file to see the 'Read PDF Aloud' option."
EOF

chmod +x installer/install.sh

# Create DMG (requires create-dmg tool)
if command -v create-dmg &> /dev/null; then
    echo "Creating DMG installer..."
    create-dmg \
        --volname "PDF Speak Easy Installer" \
        --volicon "icon.icns" \
        --window-pos 200 120 \
        --window-size 600 300 \
        --icon-size 100 \
        --icon "PDF Speak Easy.app" 175 120 \
        --hide-extension "PDF Speak Easy.app" \
        --app-drop-link 425 120 \
        "PDF-Speak-Easy-Installer.dmg" \
        "installer/"
else
    echo "create-dmg not found. Creating zip archive instead..."
    cd installer
    zip -r ../PDF-Speak-Easy-Installer.zip .
    cd ..
fi

echo "Build complete!"
echo "Installer available as PDF-Speak-Easy-Installer.dmg or PDF-Speak-Easy-Installer.zip"