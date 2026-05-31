# Nuitka-GUI-with-Embedded-AI-Error-Diagnostics
![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)
[![Nuitka](https://img.shields.io/badge/Nuitka-2.0+-green.svg)](https://nuitka.net/)
Taran Build Master is a professional desktop application that provides a graphical user interface for compiling Python scripts into standalone Windows executables using Nuitka. It integrates a pre‑trained machine learning model (39 error classes) that automatically detects compilation failures and suggests – or even applies – corrective measures.

"Enjoying this project? Buy me a coffee 🚀"
[![Donate](https://img.shields.io/badge/Donate-PayPal-blue.svg)](https://www.paypal.com/donate/?hosted_button_id=S4AH7LV44BT9N)

Support the project! Give it a ⭐ if you find it useful.
## Support the project! Give it a ⭐ if you find it useful.

[![Star on GitHub](https://img.shields.io/github/stars/yan4ikxxx-wq/Nuitka-GUI-with-Embedded-AI-Error-Diagnostics?style=social)](https://github.com/yan4ikxxx-wq/Nuitka-GUI-with-Embedded-AI-Error-Diagnostics)
<img width="1309" height="800" alt="4" src="https://github.com/user-attachments/assets/642f4851-9f9e-451d-8640-84b659aa3c3c" />
<img width="560" height="1848" alt="3" src="https://github.com/user-attachments/assets/6839063a-3f4a-410d-9d1d-5bc3d7ba7e61" />
<img width="560" height="1903" alt="2" src="https://github.com/user-attachments/assets/b386900e-eaad-411b-a627-381a178fc618" />
<img width="1024" height="964" alt="1" src="https://github.com/user-attachments/assets/df3f61ac-b80c-41d0-b9fd-6ff824486cac" />
Support the project! Give it a ⭐ if you find it useful.
## Support the project! Give it a ⭐ if you find it useful.

[![Star on GitHub](https://img.shields.io/github/stars/yan4ikxxx-wq/Nuitka-GUI-with-Embedded-AI-Error-Diagnostics?style=social)](https://github.com/yan4ikxxx-wq/Nuitka-GUI-with-Embedded-AI-Error-Diagnostics)
 Key Features

 ![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)
[![Nuitka](https://img.shields.io/badge/Nuitka-2.0+-green.svg)](https://nuitka.net/)

Full Nuitka control – Onefile / Standalone, console mode, custom icon, compiler selection (MSVC, MinGW, Auto), LTO, ccache, and more.

Plugin management – Qt, Tkinter, Torch, NumPy.

Asset bundling – Add any files/folders via --include-data-file / --include-data-dir.

AI‑powered error diagnosis – 39 error classes, confidence threshold (≥60%), and automatic fix suggestions (auto‑switch compiler, disable LTO, exclude heavy libs, etc.).

Safety features – recursive auto‑fix protection (max 2 attempts per error type), context‑aware false‑positive filters.

Large error database integration – optional nuitka_errors_150000.json for fallback semantic matching when model confidence is low.

Multi‑threaded – builds run in background without freezing the GUI.

System tray – minimise to tray with pystray.

Unicode Path Defender – automatically redirects temp directories when Cyrillic or special characters are detected.

Smart log decoding – handles CP1251/CP866 encodings to avoid corrupted UTF‑8 output.

No black console window – final .exe runs as a pure GUI application.

## 💻 OS Compatibility & System Requirements

This application is specifically designed and optimized for the **Windows** ecosystem, as it focuses on generating standalone Windows executables (`.exe`).

## 💻 OS Compatibility & System Requirements

This application is specifically designed and optimized for the **Windows** ecosystem, as it focuses on generating standalone Windows executables (`.exe`).

### ✅ Supported Operating Systems
- **Windows 11** – fully supported and recommended  
- **Windows 10** – fully supported  
- **Windows 8.1 / 8 / 7** – supported when using a compiled `TaranBuildMaster.exe` (or running from source with Python 3.8+ and a compatible C++ compiler)

### 🧱 Target Architecture
- **64‑bit (x64)** – recommended; the pre‑compiled `TaranBuildMaster.exe` is built for x64.  
- **32‑bit (x86)** – supported only when running from source using a 32‑bit Python interpreter and a 32‑bit C++ compiler (e.g., MinGW‑w32).

### ⚠️ Important Platform Notes
- 🐧 **Linux / 🍏 macOS:** The current GUI and compilation pipeline (including Windows‑specific features like *Unicode Path Defender*, system tray integration, `taskkill`, and `--windows-*` Nuitka flags) are **not supported** on Linux or macOS. The tool is intended strictly for Windows deployment.  
- **Wine:** Running the compiled `.exe` under Wine may work, but it is not tested nor officially supported.
🚀 Getting Started
Option 1: Download the compiled executable
Download the latest TaranBuildMaster.exe from the Releases page.

Place it in any folder (no installation required).

Run TaranBuildMaster.exe.

The .exe is fully self‑contained (includes the AI model). No Python environment is needed.

Option 2: Build from source
Prerequisites
Python 3.9 or higher

Pip

A C++ compiler (MSVC recommended, or MinGW‑w64)

Install dependencies
bash
pip install nuitka scikit-learn numpy pillow pystray

Note: scikit-learn is only needed if you want to load an external model; the embedded model works without it.

Clone the repository
bash

git clone https://github.com/yan4ikxxx-wq/Nuitka-GUI-with-Embedded-AI-Error-Diagnostics.git
cd Nuitka-GUI-with-Embedded-AI-Error-Diagnostics

Run from source
bash

python build_manager_NUITKA.py

## How to Compile (Using Nuitka)

To compile this project into a standalone executable on any Windows machine, make sure you have Python and Nuitka installed, then run the following command from the project root directory:

```bash
python -m nuitka --onefile --windows-console-mode=disable --windows-icon-from-ico=TARAN.ico --jobs=7 --assume-yes-for-downloads --lto=no --disable-ccache --prefer-source-code --mingw64 --enable-plugin=tk-inter --enable-plugin=numpy --output-dir=dist build_manager_NUITKA.py

The compiled .exe will appear in build_manager_NUITKA.dist/

taran-build-master/
├── build_manager_NUITKA.py     # Main application script
├── TARAN.ico                   # Application icon (used by window and tray)
├── light_error_model.pkl       # Optional external model (if not embedded)
├── nuitka_errors_150000.json   # Optional large error database
└── README.md

If you embed the AI model as Base64 (recommended), the .pkl file is not required.

🖥️ Usage
Select your Python script – click Browse and choose the .py file you want to compile.

Adjust compilation settings (Onefile, Standalone, console, icon, compiler, plugins, etc.).

(Optional) Exclude heavy libraries – use the ANALYSIS & EXCLUDES panel to avoid bloating the output.

(Optional) Add extra files/folders – they will be bundled via --include-data-file / --include-data-dir.

Click START BUILD (DIAGNOSTIC) – the compilation runs in the background.

If an error occurs, the AI assistant will:

Show the predicted error class and confidence.

Suggest a fix (or apply it automatically if Auto‑fix settings is enabled).

Fall back to the 150k error database for low‑confidence predictions.

After a successful build, the output is placed in the dist folder (inside your script’s directory).

🤖 AI Diagnostics – How It Works
The model is loaded from embedded Base64 (or an external .pkl file).

predict_with_confidence() uses predict_proba() when available; otherwise falls back to predict().

Confidence threshold is 0.60 – below that, the assistant does not act (except for critical failures).

A semantic fallback searches the 150k‑sample JSON database if confidence is low.

Contextual filters suppress false positives (e.g., Tkinter bloat warnings when Tkinter is not imported).

Auto‑fix changes compiler settings, plugins, or other options (max 2 attempts per error type per build session).

🛠️ Command‑line compilation (advanced)
You can also generate a .bat script by clicking GENERATE BAT FILE – it will contain the exact Nuitka command with all your GUI settings.

Example manual Nuitka command for a complex project:

bash
python -m nuitka --standalone --onefile --windows-console-mode=disable --windows-icon-from-ico=myicon.ico --enable-plugin=tk-inter --include-data-file=my_data.json=my_data.json --lto=no --disable-ccache my_script.py
📄 License
This project is licensed under the Apache 2.0 – see the LICENSE file for details.

Built for Python developers who need a smart, self‑tuning Nuitka frontend.

## Development & Acknowledgments
The source code of this project was co-developed using Google Gemini and DeepSeek AI models to optimize algorithms and streamline logic. 
The application is compiled into a standalone executable using the Nuitka compiler.

Contributing
Contributions are welcome! If you have a feature request, bug report, or pull request, please feel free to open an issue or submit a PR.

Support
If you encounter any problems, please open an issue. For updates and discussions, follow the repository.
