import sys
import os
import pystray
from PIL import Image
import threading
import ctypes  # Using the standard lightweight module instead of heavy libraries like torch

def get_resource_path(relative_path):
    """
    Returns the absolute path to the resource.
    Works both in development mode (IDE) and when frozen (EXE).
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def check_device():
    """Fast and lightweight CUDA availability check via the system driver."""
    try:
        # Attempting to load the NVIDIA CUDA system driver library
        cuda = ctypes.windll.LoadLibrary('nvcuda.dll')
        num_devices = ctypes.c_int()
        # Getting the number of active CUDA devices
        result = cuda.cuDeviceGetCount(ctypes.byref(num_devices))
        if result == 0 and num_devices.value > 0:
            device = "cuda"
        else:
            device = "cpu"
    except Exception:
        device = "cpu"

    print(f"--- Initialization device: {device} ---")
    return device

def setup_tray(icon_filename="TARAN.ico"):
    """Sets up the system tray icon using the correct resource paths."""
    icon_path = get_resource_path(icon_filename)

    if not os.path.exists(icon_path):
        print(f"Error: Icon not found at path {icon_path}")
        return

    image = Image.open(icon_path)

    def on_quit(icon, item):
        print("Shutting down...")
        icon.stop()
        os._exit(0)

    menu = pystray.Menu(pystray.MenuItem("Exit", on_quit))
    icon = pystray.Icon("TaranCore", image, "Taran Application", menu)
    icon.run()


if __name__ == "__main__":
    # 1. Quick hardware diagnostics without importing heavy libraries
    device = check_device()

    print("TaranCore application started successfully.")

    # 2. Starting the system tray in a separate thread
    tray_thread = threading.Thread(target=setup_tray, args=("TARAN.ico",), daemon=True)
    tray_thread.start()

    try:
        while True:
            # Main application loop
            pass
    except KeyboardInterrupt:
        sys.exit()
