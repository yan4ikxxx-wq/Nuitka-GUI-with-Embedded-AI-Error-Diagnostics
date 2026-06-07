"""
Copyright (c) 2026 [NADIZIK]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

DISCLAIMER OF LIABILITY (CRITICAL WARNING):
-------------------------------------------
THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

THIS SOFTWARE CONTAINS CODE AND LOGIC ASSISTED BY ARTIFICIAL INTELLIGENCE
(GOOGLE GEMINI & DEEPSEEK) AND INVOLVES CHEMICAL COMPUTATIONS/AUTOMATION.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE, THE USE
OF THE SOFTWARE, OR ANY INCORRECT CHEMICAL DATA, CALCULATIONS, OR MALFUNCTIONS
RESULTING FROM THE COMPILED EXECUTABLE.

USE AT YOUR OWN RISK.
"""  # -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog
import os
import subprocess
import sys
import threading
import time
import queue
import ast
import multiprocessing
import shutil
import pystray
import base64
import io
import math
import json
import ctypes
from PIL import Image
import sklearn
import sklearn.pipeline
import sklearn.feature_extraction.text
import sklearn.svm
import numpy
import scipy

# ==============================================================================
# EMBEDDED AI MODEL (OPTIONAL – paste Base64 string here to avoid external .pkl)
# ==============================================================================
BUILTIN_MODEL_BASE64 = ""
# ==============================================================================

# Dictionary mapping all 39 model classes to English diagnostics and automatic fixes
MODEL_DIAGNOSTICS = {
    "Bloatware Warning / Excessive Size": {
        "desc": "The executable size is too large. Nuitka is including unnecessary dependencies.",
        "action": "Use the 'ANALYSIS & EXCLUDES' panel to exclude heavy libraries using (--nofollow-import-to).",
        "fix": lambda app: app.open_selection()
    },
    "Bloatware: NumPy/SciPy": {
        "desc": "Heavy NumPy/SciPy package detected.",
        "action": "If your script does not require mathematical computations directly, exclude NumPy in the analysis window.",
        "fix": lambda app: app.open_selection()
    },
    "Bloatware: PyQt5/PySide6": {
        "desc": "Heavy Qt framework detected.",
        "action": "Disable unused Qt plugins or exclude unnecessary submodules.",
        "fix": lambda app: app.plugin_qt_var.set(False)
    },
    "Bloatware: PyTorch/TensorFlow": {
        "desc": "Build size is critically bloated due to deep learning libraries.",
        "action": "Enable 'Auto-disable Torch JIT' to reduce footprint or exclude PyTorch completely.",
        "fix": lambda app: app.torch_jit_var.set(True)
    },
    "Bloatware: Tkinter/Tcl": {
        "desc": "Tkinter dependencies are increasing the distribution size.",
        "action": "If your UI is not written in Tkinter, disable the 'Tkinter Interface' plugin.",
        "fix": lambda app: app.plugin_tkinter_var.set(False)
    },
    "Code Signing Failure (Windows)": {
        "desc": "Failed to digitally sign the resulting executable file.",
        "action": "Ensure the signtool utility is configured correctly, or disable signing in the advanced settings.",
        "fix": None
    },
    "Compilation Slows due to Debug Symbols": {
        "desc": "Compilation is slowed down by debug symbol generation.",
        "action": "Enable the fast build option without LTO and disable debug output.",
        "fix": lambda app: app.no_lto_var.set(True)
    },
    "Cython Module Compilation Failure": {
        "desc": "Failed to compile a third-party Cython module.",
        "action": "It is recommended to exclude this module from compilation (--nofollow-import-to) and keep it as a raw .py file.",
        "fix": lambda app: app.open_selection()
    },
    "Environment Variable Missing (PYTHONPATH)": {
        "desc": "The critical PYTHONPATH environment variable was not found.",
        "action": "Add your script path to the system's PYTHONPATH environment variable.",
        "fix": None
    },
    "Indentation Error": {
        "desc": "IndentationError detected in Python source code.",
        "action": "Open the project source code and fix the indentation structure (spaces/tabs).",
        "fix": None
    },
    "Linker Error: LTO (Link Time Optimization)": {
        "desc": "Linker error occurred during Link Time Optimization (LTO). This is common on older PCs or compilers.",
        "action": "Enable the 'Fast Build (Disable LTO)' option (sets --lto=no) to resolve linker hangs.",
        "fix": lambda app: app.no_lto_var.set(True)
    },
    "Linux: Missing ldconfig or libc.so.6": {
        "desc": "Linux system is missing the ldconfig utility or glibc library.",
        "action": "Install the libc6 / ldconfig package using your package manager (apt/yum).",
        "fix": None
    },
    "Long Path Issue (Windows)": {
        "desc": "The maximum filesystem path length (260 characters limit) has been exceeded on Windows.",
        "action": "Enable Long Paths in the Windows Registry, or move your project to the root folder (e.g., C:\\Build).",
        "fix": None
    },
    "Missing Compiler (Clang)": {
        "desc": "The Clang compiler requested by the builder is missing from the system.",
        "action": "Install Clang or switch the 'Compiler' setting to 'MSVC' or 'Auto'.",
        "fix": lambda app: app.compiler_var.set("Auto")
    },
    "Missing Compiler (GCC)": {
        "desc": "The GCC (MinGW) compiler is missing from the system.",
        "action": "Install MinGW (Winlibs) or switch the compiler setting to MSVC.",
        "fix": lambda app: app.compiler_var.set("MSVC (Recommended)")
    },
    "Missing Compiler (MSVC)": {
        "desc": "Microsoft Visual C++ (MSVC) compiler was not found on the system.",
        "action": "Install Visual Studio Build Tools with the 'Desktop development with C++' workload, or switch to 'MinGW (Winlibs)'.",
        "fix": lambda app: app.compiler_var.set("MinGW (Winlibs)")
    },
    "Missing Compiler (Windows)": {
        "desc": "No compatible C++ compilers were found on Windows.",
        "action": "Nuitka requires a C++ compiler. Set the compiler to 'Auto' (Nuitka will automatically download MinGW).",
        "fix": lambda app: app.compiler_var.set("Auto")
    },
    "Missing Python Module": {
        "desc": "A required module is missing from the current Python environment.",
        "action": "Install the missing module via terminal: pip install <module_name>.",
        "fix": None
    },
    "Missing System Tool: Dependency Walker (Windows)": {
        "desc": "Dependency Walker tool is missing for DLL analysis.",
        "action": "Nuitka will download it automatically during the first build. Ensure you have an internet connection.",
        "fix": None
    },
    "Missing System Tool: ccache": {
        "desc": "ccache build caching tool is missing.",
        "action": "Disable 'Use Build Cache (ccache)' to prevent warnings, or install ccache.",
        "fix": lambda app: app.use_ccache_var.set(False)
    },
    "Missing System Tool: distcc": {
        "desc": "distcc distributed compilation tool is missing.",
        "action": "Ensure distributed building is not forced in your scons configuration parameters.",
        "fix": None
    },
    "Missing setuptools / distutils": {
        "desc": "The setuptools library is missing from the Python environment.",
        "action": "Install it in your environment: pip install setuptools.",
        "fix": None
    },
    "Multiprocessing Fork Issue": {
        "desc": "Process forking conflict (multiprocessing) occurred when launching the compiled application.",
        "action": "Add a call to `multiprocessing.freeze_support()` immediately below `if __name__ == '__main__':` in your script.",
        "fix": None
    },
    "Namespace Package Conflict": {
        "desc": "Namespace package import conflict occurred during packaging.",
        "action": "Use the Nuitka option `--include-package` to force the entire package inclusion.",
        "fix": None
    },
    "Nuitka Version Mismatch": {
        "desc": "Your Nuitka version is outdated or conflicts with the installed Python environment.",
        "action": "Upgrade Nuitka using: pip install --upgrade nuitka.",
        "fix": None
    },
    "Onefile Temp Directory Issue": {
        "desc": "Failed to unpack temporary files in Onefile mode.",
        "action": "Try building the project in Standalone directory mode by disabling 'Onefile Mode'.",
        "fix": lambda app: app.onefile_var.set(False)
    },
    "Permission Denied (Unix)": {
        "desc": "Permission denied error on Unix-based operating system.",
        "action": "Run the builder with sudo privileges or grant write permissions to the target folder: chmod +w.",
        "fix": None
    },
    "Permission Denied (Windows)": {
        "desc": "Access denied. The file is locked by another process or requires administrator privileges.",
        "action": "Elevating privileges to Administrator dynamically. Closing current master...",
        "fix": lambda app: app.relaunch_as_admin() if not app.is_admin() else None
    },
    "Plugin Issue: Matplotlib Backend": {
        "desc": "Failed to render Matplotlib charts inside the compiled executable.",
        "action": "Enable the `--enable-plugin=matplotlib` option, or ensure the backend configuration is correct.",
        "fix": None
    },
    "Plugin Issue: PyQt5 (Designer plugins)": {
        "desc": "Qt Designer plugin conflict occurred during assembly.",
        "action": "Enable the Qt plugin in the right panel of the interface.",
        "fix": lambda app: app.plugin_qt_var.set(True)
    },
    "Plugin: PyInstaller Compatibility (--follow-imports)": {
        "desc": "Nuitka import parameters conflict with PyInstaller syntax.",
        "action": "Avoid using PyInstaller config files. Use standard Nuitka import flags instead.",
        "fix": None
    },
    "Recursion Depth Exceeded": {
        "desc": "Maximum recursion depth exceeded during Nuitka static analysis.",
        "action": "Optimize your script import structure and avoid cyclic dependencies.",
        "fix": None
    },
    "Relative Import Outside Package": {
        "desc": "Relative import error occurred outside of the package hierarchy.",
        "action": "Convert relative imports like 'from . import module' to absolute imports.",
        "fix": None
    },
    "Standalone Mode Crash (DLL Dependencies)": {
        "desc": "The compiled program crashed due to missing required DLL libraries.",
        "action": "Ensure Standalone mode is active. Copy the missing DLL files to the dist folder manually.",
        "fix": lambda app: app.standalone_var.set(True)
    },
    "Standalone Mode Crash (Missing Data Files)": {
        "desc": "The program failed to start because of missing data assets (images, configs, text files).",
        "action": "Place data files next to the compiled binary, or use Nuitka's `--include-data-files` option.",
        "fix": None
    },
    "Syntax Error": {
        "desc": "Syntax error detected in the target Python script.",
        "action": "Verify that your script works properly by running it directly using a Python interpreter.",
        "fix": None
    },
    "Unicode/Encoding Error in Source": {
        "desc": "Character encoding error detected in Python source script.",
        "action": "Resave your .py file utilizing UTF-8 character encoding.",
        "fix": None
    },
    "macOS Codesign & Notarization": {
        "desc": "Codesigning is required on the macOS platform.",
        "action": "Ensure you have Xcode Command Line Tools installed and a valid Apple Developer profile configured.",
        "fix": None
    },
    "zstandard Compression Error (Onefile)": {
        "desc": "Onefile archive compression error. The 'zstandard' library is missing.",
        "action": "Run 'pip install zstandard' to install the compression module.",
        "fix": lambda app: app.onefile_var.set(False)
    }
}

class TaranBuildMaster:
    """Nuitka compiler GUI suite featuring Path Defenders, Admin Elevation, and strict ML diagnostic filters."""

    def __init__(self, root):
        self.root = root
        self.root.title("Taran Build Master [Nuitka Suite + Embedded AI]")
        self.root.geometry("1180x950")
        self.root.minsize(950, 750)

        self.log_queue = queue.Queue()
        self.clf = None
        self.diagnosed_topics = set()
        self.auto_fix_counts = {}
        self.has_placeholder = False
        self.dataset_data = None
        self.db_status_var = tk.StringVar(value="Checking...")

        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                self.base_resource_path = sys._MEIPASS
            else:
                self.base_resource_path = os.path.dirname(sys.executable)
        elif '__compiled__' in globals():
            self.base_resource_path = os.path.dirname(sys.argv[0])
        else:
            self.base_resource_path = os.path.dirname(os.path.abspath(__file__))

        default_ico = "TARAN.ico"
        possible_ico_path = os.path.join(self.base_resource_path, default_ico)
        if not os.path.exists(possible_ico_path):
            possible_ico_path = os.path.join(os.getcwd(), default_ico)

        self.launch_path = os.getcwd()

        # Build Variables
        self.target_script = tk.StringVar(value="")
        self.icon_path = tk.StringVar(value=possible_ico_path if os.path.exists(possible_ico_path) else "")
        self.onefile_var = tk.BooleanVar(value=True)
        self.standalone_var = tk.BooleanVar(value=True)
        self.console_var = tk.BooleanVar(value=True)

        # Optimization Variables
        self.no_lto_var = tk.BooleanVar(value=True)
        self.use_ccache_var = tk.BooleanVar(value=True)
        self.compiler_var = tk.StringVar(value="Auto")
        self.torch_jit_var = tk.BooleanVar(value=True)
        self.prefer_source_var = tk.BooleanVar(value=False)

        # Plugin Variables
        self.plugin_qt_var = tk.BooleanVar(value=False)
        self.plugin_tkinter_var = tk.BooleanVar(value=False)
        self.plugin_torch_var = tk.BooleanVar(value=False)
        self.plugin_numpy_var = tk.BooleanVar(value=False)

        self.open_dist_var = tk.BooleanVar(value=True)
        self.current_stage = tk.StringVar(value="Awaiting script selection...")

        # AI Variables
        self.model_status_var = tk.StringVar(value="Not Loaded")
        self.ai_auto_fix_var = tk.BooleanVar(value=True)

        self.excluded_libs = []
        self.detected_imports = set()

        self._setup_ui()
        self._setup_styles()
        self._start_queue_poller()
        self._init_tray_icon()
        self._autoload_ml_model()
        self._autoload_dataset_background()

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    def relaunch_as_admin(self):
        try:
            self.log("🛡️ Privilege Elevation: Requesting UAC elevation to resolve PermissionError...", "WARNING")
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            self.root.after(100, self.root.destroy)
        except Exception as e:
            self.log(f"❌ Privilege Elevation: Failed to launch elevated process: {str(e)}", "ERROR")

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

    def _setup_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # LEFT PANEL: Logging
        self.log_frame = ttk.LabelFrame(main_pane, text=f" Build Logs & Diagnostics | Console in: {self.launch_path} ")
        main_pane.add(self.log_frame, weight=3)

        self.log_area = scrolledtext.ScrolledText(
            self.log_frame, bg="#1e1e1e", fg="#ffffff", font=("Consolas", 10), insertbackground="white"
        )
        self.log_area.pack(fill="both", expand=True, padx=5, pady=5)

        self.log_area.tag_config("info", foreground="#a6e22e")
        self.log_area.tag_config("warning", foreground="#fd971f")
        self.log_area.tag_config("error", foreground="#f92672")
        self.log_area.tag_config("time", foreground="#75715e")

        # RIGHT PANEL: Controls (Canvas + Scrollbar)
        right_container = ttk.Frame(main_pane)
        main_pane.add(right_container, weight=1)

        scrollbar = ttk.Scrollbar(right_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.canvas = tk.Canvas(right_container, borderwidth=0, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.canvas.yview)

        self.ctrl_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.ctrl_frame, anchor="nw")

        self.ctrl_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Section 1: File Selection
        file_lf = ttk.LabelFrame(self.ctrl_frame, text=" Target Python Script ")
        file_lf.pack(fill="x", pady=5, padx=5)

        self.browse_btn = ttk.Button(file_lf, text="Browse...", command=self.browse_script)

        ttk.Entry(file_lf, textvariable=self.target_script, state="readonly").pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.browse_btn.pack(side="right", padx=5, pady=5)

        # Section 2: Nuitka Configuration
        cfg_lf = ttk.LabelFrame(self.ctrl_frame, text=" Nuitka Configuration ")
        cfg_lf.pack(fill="x", pady=5, padx=5)

        ttk.Checkbutton(cfg_lf, text="Onefile Mode (--onefile)", variable=self.onefile_var).pack(anchor="w", padx=10, pady=3)
        ttk.Checkbutton(cfg_lf, text="Standalone Folder (--standalone)", variable=self.standalone_var).pack(anchor="w", padx=10, pady=3)
        ttk.Checkbutton(cfg_lf, text="Show Console", variable=self.console_var).pack(anchor="w", padx=10, pady=3)

        icon_f = ttk.Frame(cfg_lf)
        icon_f.pack(fill="x", padx=10, pady=5)
        ttk.Label(icon_f, text="Icon:").pack(side="left")
        ttk.Entry(icon_f, textvariable=self.icon_path, state="readonly").pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(icon_f, text="...", command=self.browse_icon).pack(side="right")

        # Section 3: Optimization & Compiler
        opt_lf = ttk.LabelFrame(self.ctrl_frame, text=" Optimization & Compiler ")
        opt_lf.pack(fill="x", pady=5, padx=5)

        ttk.Checkbutton(opt_lf, text="Fast Build (Disable LTO for old PCs)", variable=self.no_lto_var).pack(anchor="w", padx=10, pady=3)
        ttk.Checkbutton(opt_lf, text="Use Build Cache (ccache)", variable=self.use_ccache_var).pack(anchor="w", padx=10, pady=3)
        ttk.Checkbutton(opt_lf, text="Auto-disable Torch JIT", variable=self.torch_jit_var).pack(anchor="w", padx=10, pady=3)
        ttk.Checkbutton(opt_lf, text="Prefer Source Code (--prefer-source-code)", variable=self.prefer_source_var).pack(anchor="w", padx=10, pady=3)

        comp_f = ttk.Frame(opt_lf)
        comp_f.pack(fill="x", padx=10, pady=5)
        ttk.Label(comp_f, text="Compiler:").pack(side="left", padx=2)
        compiler_menu = ttk.Combobox(
            comp_f,
            textvariable=self.compiler_var,
            values=["Auto", "MSVC (Recommended)", "MinGW (Winlibs)"],
            state="readonly"
        )
        compiler_menu.pack(side="right", fill="x", expand=True, padx=5)

        # Section 4: Nuitka Plugins
        plug_lf = ttk.LabelFrame(self.ctrl_frame, text=" Active Nuitka Plugins ")
        plug_lf.pack(fill="x", pady=5, padx=5)

        ttk.Checkbutton(plug_lf, text="Qt Support (PyQt/PySide)", variable=self.plugin_qt_var).pack(anchor="w", padx=10, pady=3)
        ttk.Checkbutton(plug_lf, text="Tkinter Interface (tk-inter)", variable=self.plugin_tkinter_var).pack(anchor="w", padx=10, pady=3)
        ttk.Checkbutton(plug_lf, text="Torch Optimization", variable=self.plugin_torch_var).pack(anchor="w", padx=10, pady=3)
        ttk.Checkbutton(plug_lf, text="NumPy Optimization", variable=self.plugin_numpy_var).pack(anchor="w", padx=10, pady=3)

        # Section 5: Included Files & Folders
        files_lf = ttk.LabelFrame(self.ctrl_frame, text=" 📁 Additional Files & Folders ")
        files_lf.pack(fill="x", pady=5, padx=5)

        self.files_listbox = tk.Listbox(files_lf, height=5, bg="#1e1e1e", fg="#ffffff", selectbackground="#3e3e3e")
        self.files_listbox.pack(fill="x", padx=10, pady=5)
        self.update_placeholder()

        btn_frame = ttk.Frame(files_lf)
        btn_frame.pack(fill="x", padx=10, pady=5)

        self.add_file_btn = ttk.Button(btn_frame, text="+ Add File", command=self.add_include_file)
        self.add_dir_btn = ttk.Button(btn_frame, text="+ Add Folder", command=self.add_include_dir)
        self.remove_btn = ttk.Button(btn_frame, text="- Remove", command=self.remove_include_item)

        self.add_file_btn.pack(side="left", fill="x", expand=True, padx=2)
        self.add_dir_btn.pack(side="left", fill="x", expand=True, padx=2)
        self.remove_btn.pack(side="left", fill="x", expand=True, padx=2)

        # SECTION 6: AI ASSISTANT
        ai_lf = ttk.LabelFrame(self.ctrl_frame, text=" 🤖 AI Assistant ")
        ai_lf.pack(fill="x", pady=5, padx=5)

        status_f = ttk.Frame(ai_lf)
        status_f.pack(fill="x", padx=10, pady=3)
        ttk.Label(status_f, text="Model Status:").pack(side="left")
        ttk.Label(status_f, textvariable=self.model_status_var, font=("Helvetica", 9, "bold"), foreground="blue").pack(side="left", padx=5)

        db_status_f = ttk.Frame(ai_lf)
        db_status_f.pack(fill="x", padx=10, pady=3)
        ttk.Label(db_status_f, text="Error Database:").pack(side="left")
        self.db_status_lbl = ttk.Label(db_status_f, textvariable=self.db_status_var, font=("Helvetica", 9, "bold"), foreground="grey")
        self.db_status_lbl.pack(side="left", padx=5)

        ttk.Button(ai_lf, text="Load External Model (.pkl)", command=self.load_model_file).pack(fill="x", pady=3, padx=10)
        ttk.Checkbutton(ai_lf, text="Auto-fix settings based on AI feedback", variable=self.ai_auto_fix_var).pack(anchor="w", padx=10, pady=3)
        ttk.Button(ai_lf, text="Run environment Auto-Tuning", command=self.auto_tune_environment_and_script).pack(fill="x", pady=3, padx=10)

        # Section 7: Actions
        act_lf = ttk.LabelFrame(self.ctrl_frame, text=" Compilation Control ")
        act_lf.pack(fill="x", pady=5, padx=5)

        self.analyze_btn = ttk.Button(act_lf, text="1. ANALYSIS & EXCLUDES", command=self.open_selection)
        self.build_btn = ttk.Button(act_lf, text="2. START BUILD (DIAGNOSTIC)", command=self.run_process)
        self.bat_btn = ttk.Button(act_lf, text="3. GENERATE BAT FILE", command=self.generate_bat)

        self.analyze_btn.pack(fill="x", pady=5, padx=10)
        self.build_btn.pack(fill="x", pady=5, padx=10)
        self.bat_btn.pack(fill="x", pady=5, padx=10)

        # Service & Logs
        aux_lf = ttk.LabelFrame(self.ctrl_frame, text=" Service & Logs ")
        aux_lf.pack(fill="x", pady=5, padx=5)

        ttk.Checkbutton(aux_lf, text="Open 'dist' folder when completed", variable=self.open_dist_var).pack(anchor="w", padx=10, pady=3)
        self.clean_btn = ttk.Button(aux_lf, text="Clean temporary .build folders", command=self.clean_temp_files)

        self.clean_btn.pack(fill="x", pady=3, padx=10)
        ttk.Button(aux_lf, text="Copy Logs to Clipboard", command=self.copy_logs).pack(fill="x", pady=2, padx=10)
        ttk.Button(aux_lf, text="Save Logs to File", command=self.save_logs).pack(fill="x", pady=2, padx=10)

        ttk.Button(self.ctrl_frame, text="EXIT", command=lambda: self._terminate_app(None, None)).pack(side="bottom", fill="x", pady=10, padx=10)
        self.root.protocol("WM_DELETE_WINDOW", lambda: self._terminate_app(None, None))

        # --- STATUS BAR ---
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10)

        ttk.Label(self.status_frame, text="Current Stage: ", font=("Helvetica", 9, "bold")).pack(side="left")
        self.status_lbl = ttk.Label(self.status_frame, textvariable=self.current_stage, font=("Helvetica", 9, "italic"), foreground="blue")
        self.status_lbl.pack(side="left")

        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

    def set_ui_state(self, state):
        """Enables or disables key UI elements during active compilation."""
        self.root.after(0, lambda: [
            self.build_btn.config(state=state),
            self.browse_btn.config(state=state),
            self.analyze_btn.config(state=state),
            self.bat_btn.config(state=state),
            self.clean_btn.config(state=state),
            self.add_file_btn.config(state=state),
            self.add_dir_btn.config(state=state),
            self.remove_btn.config(state=state),
        ])

    def update_placeholder(self):
        if self.files_listbox.size() == 0:
            self.files_listbox.insert(tk.END, "📁 [ADD ADDITIONAL FILES OR FOLDERS HERE]")
            self.files_listbox.insert(tk.END, "  These assets will be bundled directly into your build")
            self.files_listbox.insert(tk.END, "  via Nuitka --include-data-file / --include-data-dir")
            self.files_listbox.config(fg="#888888")
            self.has_placeholder = True
        else:
            self.files_listbox.config(fg="#ffffff")
            self.has_placeholder = False

    def clear_placeholder(self):
        if hasattr(self, 'has_placeholder') and self.has_placeholder:
            self.files_listbox.delete(0, tk.END)
            self.files_listbox.config(fg="#ffffff")
            self.has_placeholder = False

    def _autoload_ml_model(self):
        """Sequential loading: Embedded Base64 -> local file with fallback joblib/pickle."""
        if BUILTIN_MODEL_BASE64:
            try:
                model_bytes = base64.b64decode(BUILTIN_MODEL_BASE64)
                buffer = io.BytesIO(model_bytes)
                try:
                    import joblib
                    self.clf = joblib.load(buffer)
                except ImportError:
                    import pickle
                    self.clf = pickle.load(buffer)

                self.model_status_var.set("Embedded (Standalone)")
                self.log("🤖 AI Assistant: Successfully initialized embedded model.", "INFO")
                return
            except Exception as e:
                self.log(f"⚠️ Failed decoding embedded AI model: {str(e)}", "WARNING")

        local_dir = os.path.dirname(os.path.abspath(__file__))
        possible_names = ["light_error_model.pkl", "model.pkl", "nuitka_model.pkl", "classifier.pkl"]
        for name in possible_names:
            path_onefile = os.path.join(local_dir, name)
            path_cwd = os.path.join(self.launch_path, name)

            if os.path.exists(path_onefile):
                self._try_load_model_from_path(path_onefile)
                if self.clf is not None:
                    return
            elif os.path.exists(path_cwd):
                self._try_load_model_from_path(path_cwd)
                if self.clf is not None:
                    return
        self.log("🤖 Model not embedded or found in workspace. You can load it manually.", "WARNING")
        self.log("💡 [PRO TIP]: Enable 'Use Build Cache (ccache)' in settings.", "INFO")
        self.log("             Nuitka will download ccache automatically on first compile.", "INFO")
        self.log("             Your subsequent compilations will speed up by 10x (15-30s)!", "INFO")

    def _autoload_dataset_background(self):
        threading.Thread(target=self._load_dataset_json, daemon=True).start()

    def set_db_status(self, text, color):
        self.root.after(0, lambda: [self.db_status_var.set(text), self.db_status_lbl.config(foreground=color)])

    def _load_dataset_json(self):
        self.set_db_status("Checking...", "grey")
        local_dir = os.path.dirname(os.path.abspath(__file__))
        filename = "nuitka_errors_150000.json"
        path_onefile = os.path.join(local_dir, filename)
        path_cwd = os.path.join(self.launch_path, filename)
        target_path = None
        if os.path.exists(path_onefile):
            target_path = path_onefile
        elif os.path.exists(path_cwd):
            target_path = path_cwd
        if target_path:
            try:
                self.set_db_status("Loading...", "orange")
                self.log("📂 Database: Found nuitka_errors_150000.json. Loading database in background...", "INFO")
                with open(target_path, "r", encoding="utf-8") as f:
                    self.dataset_data = json.load(f)
                self.log("📂 Database: Successfully indexed 150k build error samples for search fallback.", "INFO")
                self.set_db_status("Ready (150k)", "green")
            except Exception as e:
                self.log(f"⚠️ Database: Failed parsing JSON database file: {str(e)}", "WARNING")
                self.set_db_status("Load Error", "red")
        else:
            self.set_db_status("Not Found", "red")

    def search_dataset_fallback(self, log_line):
        if not self.dataset_data:
            return None, 0.0
        log_words = set(log_line.lower().split())
        best_match_class = None
        best_overlap = 0
        try:
            if isinstance(self.dataset_data, list):
                for entry in self.dataset_data:
                    if isinstance(entry, dict):
                        text = entry.get("text", "") or entry.get("log", "") or entry.get("raw_log", "")
                        cls = entry.get("topic", "") or entry.get("class", "")
                    else:
                        text = str(entry)
                        cls = "Unknown"
                    if not text:
                        continue
                    entry_words = set(text.lower().split())
                    intersection = log_words.intersection(entry_words)
                    overlap_ratio = len(intersection) / len(log_words) if log_words else 0.0
                    if "scons:" in entry_words or "nuitka-reports" in entry_words:
                        continue
                    if overlap_ratio > 0.40 and len(intersection) >= 4:
                        if len(intersection) > best_overlap:
                            best_overlap = len(intersection)
                            best_match_class = cls
            if best_match_class and best_overlap > 3:
                return best_match_class, best_overlap
        except Exception:
            pass
        return None, 0.0

    def _try_load_model_from_path(self, filepath):
        """Safe model loader: tries joblib, falls back to pickle on any error."""
        loaded = False
        try:
            import joblib
            self.clf = joblib.load(filepath)
            loaded = True
            self.model_status_var.set(f"Loaded ({os.path.basename(filepath)}) - Joblib")
            self.log(f"🤖 AI model successfully loaded from {os.path.basename(filepath)} using joblib.", "INFO")
        except Exception:
            pass
        if not loaded:
            try:
                import pickle
                with open(filepath, 'rb') as f:
                    self.clf = pickle.load(f)
                self.model_status_var.set(f"Loaded ({os.path.basename(filepath)}) - Pickle")
                self.log(f"🤖 AI model successfully loaded from {os.path.basename(filepath)} using pickle fallback.", "INFO")
            except Exception as e:
                self.model_status_var.set("Load Error")
                self.log(f"❌ Failed to load model file: {str(e)}", "ERROR")
        if hasattr(self.clf, 'classes_'):
            self.log(f"🤖 Classes detected in model: {len(self.clf.classes_)}", "INFO")

    def load_model_file(self):
        filepath = filedialog.askopenfilename(
            initialdir=self.launch_path,
            filetypes=[("Pickle Files", "*.pkl"), ("All Files", "*.*")]
        )
        if filepath:
            self._try_load_model_from_path(filepath)

    def add_include_file(self):
        path = filedialog.askopenfilename(initialdir=self.launch_path)
        if path:
            self.clear_placeholder()
            self.files_listbox.insert(tk.END, path)
            self.log(f"Added asset file for packaging: {path}", "INFO")

    def add_include_dir(self):
        path = filedialog.askdirectory(initialdir=self.launch_path)
        if path:
            self.clear_placeholder()
            self.files_listbox.insert(tk.END, path)
            self.log(f"Added asset folder for packaging: {path}", "INFO")

    def remove_include_item(self):
        if hasattr(self, 'has_placeholder') and self.has_placeholder:
            return
        selected = self.files_listbox.curselection()
        if selected:
            item = self.files_listbox.get(selected[0])
            self.files_listbox.delete(selected[0])
            self.log(f"Removed packaging asset: {item}", "INFO")
            self.update_placeholder()

    def is_ascii(self, text_str):
        try:
            text_str.encode('ascii')
            return True
        except UnicodeEncodeError:
            return False

    def get_short_path(self, path):
        if sys.platform == 'win32':
            try:
                buffer_size = 1024
                buffer = ctypes.create_unicode_buffer(buffer_size)
                ctypes.windll.kernel32.GetShortPathNameW(path, buffer, buffer_size)
                return buffer.value
            except Exception:
                pass
        return path

    def terminate_existing_process(self, exe_name):
        if sys.platform == 'win32':
            try:
                subprocess.run(["taskkill", "/F", "/IM", exe_name],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            except Exception:
                pass

    def auto_tune_environment_and_script(self):
        self.log("🤖 Scanning local compiler environments...", "INFO")
        msvc_detected = False
        mingw_detected = False
        try:
            subprocess.run(["cl"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=1.5)
            msvc_detected = True
        except (FileNotFoundError, subprocess.SubprocessError):
            pass
        try:
            subprocess.run(["gcc", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=1.5)
            mingw_detected = True
        except (FileNotFoundError, subprocess.SubprocessError):
            pass
        if msvc_detected:
            self.compiler_var.set("MSVC (Recommended)")
            self.log("🤖 Environment: MSVC Compiler found. Set as primary.", "INFO")
        elif mingw_detected:
            self.compiler_var.set("MinGW (Winlibs)")
            self.log("🤖 Environment: MSVC not found. GCC (MinGW) detected. Set as primary.", "INFO")
        else:
            self.compiler_var.set("Auto")
            self.log("🤖 Environment: No compilers found in PATH. Fallback to Nuitka auto-downloader.", "WARNING")
        self.use_ccache_var.set(True)
        self.log("🤖 Optimization: Enabling 'Use Build Cache (ccache)' as highly recommended default.", "INFO")
        self.log("                 Nuitka will download ccache automatically if missing.", "INFO")
        script_path = self.target_script.get()
        if script_path:
            self.detected_imports = self.analyze_imports(script_path)
            self.auto_suggest_plugins()
            self.log("🤖 Project: Plugins successfully configured from file imports.", "INFO")
        else:
            self.log("🤖 Project: No script loaded. Awaiting file selection to tune plugins.", "WARNING")
        self.current_stage.set("System variables automatically tuned.")

    def predict_with_confidence(self, text):
        if hasattr(self.clf, "predict_proba"):
            try:
                probs = self.clf.predict_proba([text])[0]
                max_idx = probs.argmax()
                prediction = self.clf.classes_[max_idx]
                confidence = probs[max_idx]
                if math.isnan(confidence) or not math.isfinite(confidence):
                    confidence = 0.0
                return prediction, confidence
            except Exception:
                pass
        try:
            prediction = self.clf.predict([text])[0]
            return prediction, 1.0
        except Exception:
            return None, 0.0

    def run_ai_diagnostics(self, log_line):
        if self.clf is None:
            return
        lower_line = log_line.lower()
        markers = ["error", "warning", "fatal", "failed", "missing", "cannot find", "not found", "linker", "permissionerror"]
        if not any(marker in lower_line for marker in markers):
            return
        try:
            prediction = None
            confidence = 0.0
            res = self.predict_with_confidence(log_line)
            if res and res[0] is not None:
                prediction, confidence = res
            threshold = 0.60
            if confidence < threshold:
                fallback_class, overlap_score = self.search_dataset_fallback(log_line)
                if fallback_class:
                    prediction = fallback_class
                    confidence = 0.90
                else:
                    is_critical_error = any(k in lower_line for k in ["fatal", "failed", "permissionerror", "error:"])
                    if is_critical_error:
                        self.log("\n" + "=" * 60, "WARNING")
                        self.log(f"🤖 [AI ASSISTANT - Confidence {confidence:.1%}]: UNRECOGNIZED BUILD FAILURE", "WARNING")
                        self.log("📋 Description: I detected a critical build failure, but my model certainty", "WARNING")
                        self.log("                is too low to safely recommend or apply a specific fix.", "WARNING")
                        self.log("💡 Suggestion:  Please consider checking for a model update (.pkl) or", "WARNING")
                        self.log("                review the Nuitka documentation manually.", "WARNING")
                        self.log("=" * 60 + "\n", "WARNING")
                    return
            if prediction in self.diagnosed_topics:
                return
            # Contextual filters
            if prediction == "Plugin Issue: PyQt5 (Designer plugins)":
                qt_libs = ["pyqt5", "pyqt6", "pyside2", "pyside6"]
                if not any(lib in self.detected_imports for lib in qt_libs):
                    return
            if prediction == "Linker Error: LTO (Link Time Optimization)":
                if self.no_lto_var.get() is True:
                    return
            if prediction == "Missing System Tool: ccache":
                if self.use_ccache_var.get() is False:
                    return
            if prediction == "Bloatware: Tkinter/Tcl":
                if "tkinter" not in self.detected_imports and self.plugin_tkinter_var.get() is False:
                    return
            if prediction == "Bloatware: PyTorch/TensorFlow":
                if "torch" not in self.detected_imports and "tensorflow" not in self.detected_imports:
                    return
            if prediction == "Missing Python Module":
                if "dll" in lower_line or "runtime" in lower_line or "windows" in lower_line:
                    return
            if "pyinstaller" in prediction.lower():
                if "icon" in lower_line or "postprocessing" in lower_line:
                    return
            if "standalone mode crash" in prediction.lower():
                if "nuitka-options" in lower_line or "included data file" in lower_line:
                    return
            if prediction == "Plugin Issue: Matplotlib Backend":
                if "matplotlib" not in self.detected_imports and "matplotlib" not in lower_line:
                    return
            if prediction == "Compilation Slows due to Debug Symbols":
                if not any(k in lower_line for k in ["debug", "symbol", "slow", "cl.exe"]):
                    return
            if prediction == "Multiprocessing Fork Issue":
                if not any(k in lower_line for k in ["multiprocessing", "fork", "freeze_support"]):
                    return
            if prediction in MODEL_DIAGNOSTICS:
                self.diagnosed_topics.add(prediction)
                info = MODEL_DIAGNOSTICS[prediction]
                self.log("\n" + "=" * 60, "WARNING")
                self.log(f"🤖 [AI DIAGNOSIS - Confidence {confidence:.1%}]: Compilation warning or error classified!", "WARNING")
                self.log(f"📌 Class: {prediction}", "WARNING")
                self.log(f"📋 Details: {info['desc']}", "WARNING")
                self.log(f"💡 Recommendation (What to do): {info['action']}", "WARNING")
                if self.ai_auto_fix_var.get() and info['fix'] is not None:
                    fix_count = self.auto_fix_counts.get(prediction, 0)
                    if fix_count >= 2:
                        self.log(f"⚠️ [AI ASSISTANT]: Auto-Fix limit reached for '{prediction}'. Bypassing to prevent infinite loops.", "WARNING")
                    else:
                        self.auto_fix_counts[prediction] = fix_count + 1
                        self.log(f"🛠️ Auto-Fix: Applying recommended GUI adjustment (Attempt {fix_count + 1}/2)...", "INFO")
                        self.root.after(0, lambda: info['fix'](self))
                self.log("=" * 60 + "\n", "WARNING")
        except Exception:
            pass

    def _init_tray_icon(self):
        ico_path = self.icon_path.get()
        if not ico_path or not os.path.exists(ico_path):
            img = Image.new('RGB', (64, 64), color=(30, 30, 30))
        else:
            try:
                img = Image.open(ico_path)
            except Exception:
                img = Image.new('RGB', (64, 64), color=(249, 38, 114))
        menu = pystray.Menu(
            pystray.MenuItem("Restore Window", self._restore_window, default=True),
            pystray.MenuItem("Exit App", self._terminate_app)
        )
        self.tray_icon = pystray.Icon("TaranBuildMaster", img, "Taran Build Master", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _restore_window(self, icon, item):
        self.root.after(0, lambda: self.root.deiconify())
        self.root.after(0, lambda: self.root.lift())

    def _terminate_app(self, icon, item):
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.root.after(0, self.root.quit)

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def browse_script(self):
        path = filedialog.askopenfilename(
            initialdir=self.launch_path,
            filetypes=[("Python Files", "*.py")]
        )
        if path:
            self.target_script.set(path)
            self.launch_path = os.path.dirname(path)
            self.log(f"Target script loaded: {path}", "INFO")
            self.auto_tune_environment_and_script()

    def browse_icon(self):
        path = filedialog.askopenfilename(
            initialdir=self.launch_path,
            filetypes=[("Icon Files", "*.ico")]
        )
        if path:
            self.icon_path.set(path)
            self.log(f"Icon path set: {path}", "INFO")

    def auto_suggest_plugins(self):
        self.plugin_qt_var.set(any(x in self.detected_imports for x in ["pyqt5", "pyqt6", "pyside2", "pyside6"]))
        self.plugin_tkinter_var.set("tkinter" in self.detected_imports)
        self.plugin_torch_var.set("torch" in self.detected_imports)
        self.plugin_numpy_var.set("numpy" in self.detected_imports)
        self.current_stage.set("Script analyzed. Ready to build.")

    def analyze_imports(self, file_path):
        if not file_path or not os.path.exists(file_path):
            return set()
        imported_modules = set()
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imported_modules.add(name.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imported_modules.add(node.module.split('.')[0])
        except Exception as e:
            self.log(f"Failed parsing script imports: {str(e)}", "WARNING")
        return imported_modules

    def open_selection(self):
        script_path = self.target_script.get()
        if not script_path:
            messagebox.showwarning("Warning", "Select a script first to analyze imports.")
            return
        detected_imports = self.analyze_imports(script_path)
        win = tk.Toplevel(self.root)
        win.title("Nuitka Excludes Panel")
        win.geometry("400x350")
        win.transient(self.root)
        win.grab_set()
        ttk.Label(win, text="Check heavy frameworks to EXCLUDE from build:", font=("Helvetica", 10, "bold")).pack(pady=10)
        candidates = ["numpy", "scipy", "sympy", "pandas", "torch", "matplotlib", "pyqt5", "pyside2", "pyside6"]
        self.vars = {}
        frame = ttk.Frame(win)
        frame.pack(fill="both", expand=True, padx=15, pady=5)
        for lib in candidates:
            default_value = lib not in detected_imports
            self.vars[lib] = tk.BooleanVar(value=default_value)
            state_text = " (Not imported)" if default_value else " (Import detected!)"
            cb = ttk.Checkbutton(frame, text=f"{lib}{state_text}", variable=self.vars[lib])
            cb.pack(anchor="w", pady=2)
        ttk.Button(win, text="Apply Changes", command=lambda: self.apply_selection(win)).pack(pady=10)

    def apply_selection(self, win):
        self.excluded_libs = [f"--nofollow-import-to={m}" for m, v in self.vars.items() if v.get()]
        self.log(f"Exclusion parameters set: {self.excluded_libs}", "INFO")
        win.destroy()

    def _build_cmd_args(self):
        script_path = self.target_script.get()
        if not script_path:
            return None
        working_dir = os.path.dirname(script_path)
        script_name = os.path.basename(script_path)

        # Hybrid Python interpreter detection strategy
        if getattr(sys, 'frozen', False):
            # 1. Check if global Python is available in the system PATH
            if shutil.which("python"):
                python_exe = "python"
            else:
                # 2. If not, look for a local portable Python environment adjacent to the .exe
                exe_dir = os.path.dirname(sys.executable)
                portable_path = os.path.join(exe_dir, "python_portable", "python.exe")

                if os.path.exists(portable_path):
                    python_exe = portable_path
                else:
                    # 3. Fallback to system command if everything else fails
                    python_exe = "python"
        else:
            # Standard execution within an IDE / development environment
            python_exe = sys.executable

        # Construct the base Nuitka compilation command
        cmd = [python_exe, "-u", "-m", "nuitka"]

        if self.standalone_var.get():
            cmd.append("--standalone")
        if self.onefile_var.get():
            cmd.append("--onefile")
        if not self.console_var.get():
            cmd.append("--windows-console-mode=disable")
        else:
            cmd.append("--windows-console-mode=force")
        if self.icon_path.get():
            cmd.append(f"--windows-icon-from-ico={self.icon_path.get()}")
        cpu_count = multiprocessing.cpu_count()
        cmd.append(f"--jobs={max(1, cpu_count - 1)}")
        cmd.append("--assume-yes-for-downloads")
        if self.no_lto_var.get():
            cmd.append("--lto=no")
        if not self.use_ccache_var.get():
            cmd.append("--disable-ccache")
        if self.prefer_source_var.get():
            cmd.append("--prefer-source-code")
        comp_choice = self.compiler_var.get()
        if "MSVC" in comp_choice:
            cmd.append("--msvc=latest")
        elif "MinGW" in comp_choice:
            cmd.append("--mingw64")
        if self.plugin_qt_var.get():
            if "pyside6" in self.detected_imports:
                cmd.append("--enable-plugin=pyside6")
            elif "pyqt6" in self.detected_imports:
                cmd.append("--enable-plugin=pyqt6")
            elif "pyside2" in self.detected_imports:
                cmd.append("--enable-plugin=pyside2")
            elif "pyqt5" in self.detected_imports:
                cmd.append("--enable-plugin=pyqt5")
        if self.plugin_tkinter_var.get():
            cmd.append("--enable-plugin=tk-inter")
        if self.plugin_torch_var.get():
            cmd.append("--enable-plugin=torch")
        if self.plugin_numpy_var.get():
            cmd.append("--enable-plugin=numpy")
        if self.torch_jit_var.get() and "torch" in self.detected_imports:
            cmd.append("--module-parameter=torch-disable-jit=yes")
        if not self.has_placeholder:
            for i in range(self.files_listbox.size()):
                item_path = self.files_listbox.get(i)
                if os.path.exists(item_path):
                    basename = os.path.basename(item_path)
                    if os.path.isdir(item_path):
                        cmd.append(f"--include-data-dir={item_path}={basename}")
                    else:
                        cmd.append(f"--include-data-file={item_path}={basename}")
        cmd.extend(["--output-dir=dist", "--show-scons"])
        cmd.extend(self.excluded_libs)
        cmd.append(script_name)
        return cmd, working_dir

    def generate_bat(self):
        res = self._build_cmd_args()
        if not res:
            messagebox.showwarning("Warning", "Select target script first.")
            return
        cmd, working_dir = res
        bat_path = os.path.join(working_dir, "build_cmd.bat")
        try:
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write("@echo off\n")
                f.write(f"cd /d \"{working_dir}\"\n")
                f.write(" ".join(cmd) + "\n")
                f.write("pause")
            self.log(f"File generated: {bat_path}.", "INFO")
        except Exception as e:
            self.log(f"Failed to generate bat file: {str(e)}", "ERROR")

    def clean_temp_files(self):
        script_path = self.target_script.get()
        if not script_path:
            messagebox.showwarning("Warning", "Select script first.")
            return
        working_dir = os.path.dirname(script_path)
        deleted_count = 0
        try:
            for item in os.listdir(working_dir):
                item_path = os.path.join(working_dir, item)
                if os.path.isdir(item_path) and item.endswith(".build"):
                    shutil.rmtree(item_path)
                    deleted_count += 1
            self.log(f"Cleaned temporary build folders (*.build): {deleted_count}", "INFO")
            messagebox.showinfo("Cleanup complete", f"Successfully deleted temporary folders: {deleted_count}")
        except Exception as e:
            self.log(f"Failed to remove temporary files: {str(e)}", "ERROR")

    def run_process(self):
        script_path = self.target_script.get()
        if not script_path:
            messagebox.showwarning("Warning", "Select script first.")
            return
        self.progress.start(10)
        threading.Thread(target=self.start_build, daemon=True).start()

    def parse_stage_from_log(self, line):
        lower_line = line.lower()
        if "starting python compilation" in lower_line:
            self.current_stage.set("Initializing Python Environment...")
        elif "necessitate pass" in lower_line:
            import re
            match = re.search(r"pass (\d+)", lower_line)
            pass_num = match.group(1) if match else "X"
            self.current_stage.set(f"Analyzing imports and dependencies (Pass {pass_num})...")
        elif "generating source code" in lower_line:
            self.current_stage.set("Generating C++ source files...")
        elif "running scons" in lower_line or "compiling" in lower_line:
            self.current_stage.set("Compiling C++ sources via scons...")
        elif "onefile project packaging" in lower_line or "packaging" in lower_line:
            self.current_stage.set("Packaging binary dependencies into Onefile EXE...")
        elif "completed" in lower_line and "optimization" in lower_line:
            self.current_stage.set("Python-level optimization completed successfully.")

    def start_build(self):
        self.diagnosed_topics.clear()
        self.auto_fix_counts.clear()
        self.set_ui_state("disabled")
        self.root.after(0, lambda: self.build_btn.config(text="COMPILING..."))
        res = self._build_cmd_args()
        if not res:
            self.log("Failed building command options.", "ERROR")
            self.set_ui_state("normal")
            self.root.after(0, lambda: [self.build_btn.config(text="2. START BUILD (DIAGNOSTIC)"), self.progress.stop()])
            return
        cmd, working_dir = res
        self.log("Starting Nuitka compiler...", "INFO")
        self.log(f"Working Directory: {working_dir}", "INFO")
        self.log(f"Executing: {' '.join(cmd)}", "INFO")
        self.current_stage.set("Launching build sequence...")
        # Unicode Path Defender
        if not self.is_ascii(working_dir) or not self.is_ascii(os.environ.get("TEMP", "")):
            local_temp_dir = os.path.join(working_dir, ".nuitka_tmp")
            try:
                os.makedirs(local_temp_dir, exist_ok=True)
                short_temp = self.get_short_path(local_temp_dir)
                os.environ["NUITKA_TMPDIR"] = short_temp
                self.log(f"🛡️ Unicode Path Defender: Redirected compiler temp caches locally to ASCII-safe folder: {short_temp}", "INFO")
            except Exception as e:
                self.log(f"⚠️ Path Defender: Failed to redirect NUITKA_TMPDIR: {str(e)}", "WARNING")
        # Anti-Lock Guard
        target_exe_name = os.path.basename(self.target_script.get()).replace(".py", ".exe")
        self.terminate_existing_process(target_exe_name)

        def decode_line_bytes(raw_bytes):
            for encoding in ["utf-8", "cp1251", "cp866"]:
                try:
                    return raw_bytes.decode(encoding)
                except UnicodeDecodeError:
                    continue
            return raw_bytes.decode("utf-8", errors="replace")

        try:
            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=working_dir
            )
            while True:
                line_bytes = p.stdout.readline()
                if not line_bytes:
                    break
                line_str_decoded = decode_line_bytes(line_bytes)
                if '\r' in line_str_decoded:
                    parts = line_str_decoded.split('\r')
                    for part in parts[:-1]:
                        part_clean = part.strip()
                        if part_clean:
                            self.log(part_clean, "INFO", overwrite=True)
                            self.parse_stage_from_log(part_clean)
                            self.run_ai_diagnostics(part_clean)
                    line_str_decoded = parts[-1]
                line_str = line_str_decoded.strip()
                if not line_str:
                    continue
                if "ERROR" in line_str or "Fatal" in line_str or "error:" in line_str or "PermissionError" in line_str:
                    self.log(line_str, "ERROR")
                elif "WARNING" in line_str or "Warning" in line_str:
                    self.log(line_str, "WARNING")
                else:
                    self.log(line_str, "INFO")
                self.parse_stage_from_log(line_str)
                self.run_ai_diagnostics(line_str)
            p.wait()
            if p.returncode == 0:
                self.log(f"Build completed successfully! Binaries located in: {os.path.join(working_dir, 'dist')}", "INFO")
                self.current_stage.set("Build completed successfully!")
                if self.open_dist_var.get():
                    dist_dir = os.path.join(working_dir, "dist")
                    if os.path.exists(dist_dir):
                        os.startfile(dist_dir)
            else:
                self.log(f"Compilation process closed with return code: {p.returncode}", "ERROR")
                self.current_stage.set(f"Compilation Failed (Code: {p.returncode})")
        except Exception as e:
            self.log(f"Critical build failure encountered: {str(e)}", "ERROR")
            self.current_stage.set("Critical build sequence failure.")
        finally:
            self.set_ui_state("normal")
            self.root.after(0, lambda: [self.build_btn.config(text="2. START BUILD (DIAGNOSTIC)"), self.progress.stop()])

    def log(self, msg, level="INFO", overwrite=False):
        self.log_queue.put((msg, level, overwrite))

    def _start_queue_poller(self):
        while not self.log_queue.empty():
            try:
                msg, level, overwrite = self.log_queue.get_nowait()
                tag = level.lower()
                if overwrite:
                    last_line_index = self.log_area.index("end-1c linestart")
                    self.log_area.delete(last_line_index, "end")
                    self.log_area.insert(tk.END, f"\n[{time.strftime('%H:%M:%S')}] [{level}] {msg}", tag)
                else:
                    self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] ", "time")
                    self.log_area.insert(tk.END, f"[{level}] {msg}\n", tag)
                self.log_area.see(tk.END)
            except queue.Empty:
                break
        self.root.after(100, self._start_queue_poller)

    def copy_logs(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.log_area.get(1.0, tk.END))
        messagebox.showinfo("Clipboard", "Logs copied successfully.")

    def save_logs(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.log_area.get(1.0, tk.END))
                messagebox.showinfo("Saved", f"Log file written successfully to: {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to write file: {str(e)}")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    root = tk.Tk()
    app = TaranBuildMaster(root)
    root.mainloop()
