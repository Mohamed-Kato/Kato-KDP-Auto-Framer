# Kato KDP Auto-Framer
© 2026 Mohamed Kato. All Rights Reserved.

An automated desktop application built with Python and Tkinter that perfectly formats coloring book images for Amazon KDP (Kindle Direct Publishing).

## Features
- **Auto-Crop**: Automatically detects and removes invisible white margins around your drawings.
- **Perfect Safe Zone**: Resizes the true frame of your drawing to sit perfectly within the Amazon KDP safe boundaries (0.375" margins), making it identical to professional Canva templates.
- **Auto-Rotate**: Automatically detects landscape images and rotates them to portrait orientation to fill the page optimally.
- **Unique Output**: Generates a timestamped PDF inside a `PDF/` folder so you never overwrite previous work.
- **Standalone Executable**: Comes with a `.exe` file so you don't need to install Python to run the program.

## Requirements
If you want to run from source:
```bash
pip install -r requirements.txt
```

## Usage
1. Open `Kato_KDP_Auto_Framer.exe` or run `python main.py`.
2. Click "اختيار مجلد الصور" (Select Images Folder) and pick a folder containing your grayscale `.png` or `.jpg` coloring pages.
3. Wait for the processing to finish. The app will automatically open the generated PDF and the folder containing it.

## Amazon KDP Specifications Used
- Dimensions: 8.625 x 11.25 inches (Bleed included)
- DPI: 300
- Safe Margins: 0.375 inches
- Alternating Blank Pages: Automatically inserts a blank page after every design (for single-sided printing).
