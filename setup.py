from setuptools import setup, find_packages

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': 'PDF Speak Easy',
        'CFBundleDisplayName': 'PDF Speak Easy',
        'CFBundleGetInfoString': "PDF text-to-speech reader",
        'CFBundleIdentifier': 'com.pdfspeakeasy.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'PDF Document',
                'CFBundleTypeIconFile': 'icon.icns',
                'CFBundleTypeExtensions': ['pdf'],
                'CFBundleTypeRole': 'Viewer',
            }
        ]
    }
}

setup(
    name='PDF Speak Easy',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'PyPDF2==3.0.1',
        'pyttsx3==2.90',
        'pillow==10.1.0'
    ]
)