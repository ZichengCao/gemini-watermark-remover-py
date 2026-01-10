# Gemini Watermark Remover

English | [简体中文](README.md)

---

## ⚠️ Important Disclaimer

**This project is merely a Python platform migration of [gemini-watermark-remover](https://github.com/journey-ad/gemini-watermark-remover).**

**All core principles and algorithms for watermark removal come from the original repository. The sole contribution of this project is porting this excellent technical solution to the Python platform and building a graphical user interface based on PySide6.**

The original project was developed by [@journey-ad](https://github.com/journey-ad). If you find this tool helpful, please visit the original repository to show your support and appreciation!

---

A desktop application for automatically removing watermarks from the bottom-right corner of Gemini AI generated images, with batch processing support.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## ✨ Features

- 🔍 **Auto Detection** - Intelligently identifies image size and selects appropriate watermark removal strategy
- 📦 **Batch Processing** - Process multiple images at once for improved efficiency
- 🎨 **Multiple Formats** - Supports various output formats including JPEG, PNG, and WEBP
- ⚙️ **Quality Adjustment** - Freely adjust output quality (1-100)
- 🎨 **Modern UI** - Clean and beautiful Fluent design style interface
- 🖱️ **Drag & Drop** - Drag images directly into the window for easy operation

## 📸 Screenshot

![Application Interface](assets/软件界面.png)

Clean single-page design, just drag and drop images to start processing. Support for configuring output format, quality, and output directory.

## 🚀 Quick Start

### Requirements

- Python 3.8 or higher
- Windows / macOS / Linux

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/gemini-watermarkRemover-py.git
cd gemini-watermarkRemover-py
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Download background image resources**

Due to the large size of background image files, they need to be downloaded separately:

```bash
# Download background images from the original project
# https://github.com/journey-ad/gemini-watermark-remover
```

Place the downloaded background image files in the `assets/gemini_watermark/` directory:
- `bg_48.png`
- `bg_96.png`

4. **Run the application**

```bash
python main.py
```

## 📖 Usage

1. Launch the program and drag watermarked images into the window
2. (Optional) Configure output parameters:
   - **Output Format**: Keep original / JPEG / PNG / WEBP
   - **Output Quality**: 1-100
   - **Output Directory**: Leave empty to save to the original image's directory
3. Click the "Start Processing" button
4. Wait for processing to complete. Output files will have a `_no_watermark_时间戳` suffix added

## 🛠️ Tech Stack

- **Pillow** - Python image processing library
- **PySide6** - Python bindings for Qt 6, used for building the GUI
- **PySide6-Fluent-Widgets** - Fluent design style component library
- **NumPy** - For numerical computing and image processing

## 📁 Project Structure

```
gemini-watermarkRemover-py/
├── assets/
│   ├── icon.png                 # Application icon
│   ├── 软件界面.png             # Screenshot
│   └── gemini_watermark/        # Background image resources (download separately)
├── src/
│   ├── core/
│   │   └── gemini_watermark_remover.py  # Core algorithm
│   └── ui/
│       ├── components/          # UI components
│       │   ├── file_list_widget.py
│       │   └── params_card.py
│       ├── pages/               # Pages
│       │   └── image_gemini_watermark_page.py
│       └── main_window.py       # Main window
├── main.py                      # Program entry
├── requirements.txt             # Dependencies list
├── README.md                    # Chinese documentation
└── README_EN.md                 # English documentation
```

## ⚠️ Notes

- This project only supports removing watermarks from Gemini AI generated images
- Requires pre-generated background image resource files (`bg_48.png` and `bg_96.png`)
- Output files have a `_no_watermark_时间戳` suffix added by default to avoid overwriting original files
- For learning and personal use only. Do not use for illegal purposes

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

This project is licensed under the [MIT](LICENSE) License.

## 🙏 Acknowledgments

- **Core algorithm and implementation principles**: [gemini-watermark-remover](https://github.com/journey-ad/gemini-watermark-remover) by [@journey-ad](https://github.com/journey-ad)
- **UI component library**: [PySide6-Fluent-Widgets](https://github.com/zhiyiYo/PySide-Fluent-Widgets)

## 📮 Contact

For questions or suggestions, please submit an Issue or contact via:

- GitHub Issues: [Submit Issue](https://github.com/yourusername/gemini-watermarkRemover-py/issues)

---

⭐ If this project helps you, please give it a Star to show your support!
