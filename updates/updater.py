import ctypes
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
import requests
import zipfile
import threading
import subprocess
import socket
import shutil

if getattr(sys, "frozen", False):
    updater_folder = Path(sys.executable).parent
else:
    updater_folder = Path(__file__).parent

project_root = updater_folder.parent

plugins_dir = project_root / "plugins"
plugins_dir.mkdir(parents=True, exist_ok=True)
(plugins_dir / "__init__.py").touch(exist_ok=True)

exe_for_lide = project_root / "LIDE.exe"
py_for_lide = project_root / "LIDE.py"
icon_path = project_root / "icon" / "lide.ico"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    messagebox.showerror("Error", "Run The File As Admin")
    if exe_for_lide.exists():
        subprocess.Popen([str(exe_for_lide)])
    elif py_for_lide.exists():
        subprocess.Popen([sys.executable, str(py_for_lide)])
    else:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", "Neither LIDE.exe nor LIDE.py was found.")
    sys.exit(0)

root = tk.Tk()
root.title("Plugin Updater - LIDE")
root.geometry("400x350")
root.configure(bg="#2E2E2E")

def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

center_window(root, 400, 250)

try:
    root.iconbitmap(str(icon_path))
except:
    pass

opt_a = tk.BooleanVar()
opt_b = tk.BooleanVar()
opt_c = tk.BooleanVar()

def is_connected(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except:
        return False

def show_loading(message="Downloading..."):
    global loading_win, progress, progress_label
    loading_win = tk.Toplevel(root)
    loading_win.title("Please Wait")
    loading_win.resizable(False, False)
    loading_win.configure(bg="#1E1E1E")
    
    center_window(loading_win, 360, 120)
    
    try:
        loading_win.iconbitmap(icon_path)
    except:
        pass

    loading_win.grab_set()
    
    progress_label = tk.Label(
        loading_win,
        text=message,
        bg="#1E1E1E",
        fg="#FFFFFF",
        font=("Segoe UI", 12, "bold")
    )
    progress_label.pack(pady=15)
    
    progress = ttk.Progressbar(loading_win, mode='determinate', length=320)
    progress.pack(pady=10)

def close_loading():
    try:
        loading_win.destroy()
    except:
        pass

def download_zip(url, dest_path):
    response = requests.get(url, stream=True, timeout=20)
    response.raise_for_status()
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    downloaded = 0
    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(block_size):
            f.write(chunk)
            downloaded += len(chunk)
            percent = int(downloaded * 100 / total_size) if total_size else 0
            progress['value'] = percent
            progress_label.config(text=f"Downloading... {percent}%")
            loading_win.update_idletasks()

def extract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def install_plugins(plugins):
    if not is_connected():
        messagebox.showerror("No Internet", "No internet connection detected. Please check your network.")
        return

    base_install_path = project_root / "plugins"
    base_install_path.mkdir(parents=True, exist_ok=True)

    base_path = Path(__file__).parent.resolve()
    temp_dir = base_path / "temp_plugin"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()

    for plugin in plugins:
        if plugin == "Autosave":
            url = "https://github.com/Codebyte15/LIDE_plugins/releases/download/Autosave/Autosave.zip"
        elif plugin == "Code_Runner":
            url = "https://github.com/Codebyte15/LIDE_plugins/releases/download/CodeRunner/Code_Runner.zip"
        elif plugin == "Python_Extension":
            url = "https://github.com/Codebyte15/LIDE_plugins/releases/download/Python_Extension/Python_Extension.zip"
        else:
            messagebox.showwarning("Unknown Plugin", f"'{plugin}' is not recognized.")
            continue

        try:
            show_loading(f"Downloading {plugin}...")
            zip_path = temp_dir / f"{plugin}.zip"
            download_zip(url, zip_path)
            
            progress_label.config(text=f"Extracting {plugin}...")
            loading_win.update_idletasks()
            extract_zip(zip_path, base_install_path)
            
            close_loading()
            messagebox.showinfo("Success", f"{plugin} installed successfully!")

        except requests.exceptions.RequestException:
            close_loading()
            messagebox.showerror("Download Error", f"Failed to download {plugin}. Check your internet.")
        except Exception as e:
            close_loading()
            messagebox.showerror("Error", f"Failed to install {plugin}\n{e}")

    extra_dir = base_path / "plugins"
    if extra_dir.exists():
        shutil.rmtree(extra_dir)
        
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        
    if exe_for_lide.exists():
        subprocess.Popen([str(exe_for_lide)])
    elif py_for_lide.exists():
        subprocess.Popen([sys.executable, str(py_for_lide)])
    else:
        tk.messagebox.showerror("Error", "Neither LIDE.exe nor LIDE.py was found.")
    root.destroy()

def run_install_thread():
    selected_plugins = []
    if opt_a.get(): selected_plugins.append("Autosave")
    if opt_b.get(): selected_plugins.append("Code_Runner")
    if opt_c.get(): selected_plugins.append("Python_Extension")
    if not selected_plugins:
        messagebox.showwarning("No Selection", "Please select at least one plugin.")
        return
    threading.Thread(target=install_plugins, args=(selected_plugins,), daemon=True).start()

tk.Label(
    root, text="Select Plugins to Install",
    font=("Segoe UI", 14, "bold"),
    bg="#2E2E2E", fg="#FFFFFF"
).pack(pady=10)

tk.Checkbutton(
    root, text="Autosave", variable=opt_a,
    font=('Segoe UI', 12),
    bg="#2E2E2E", fg="white",
    activebackground="#2E2E2E", activeforeground="white",
    selectcolor="#2E2E2E"
).pack(anchor='w', padx=30)

tk.Checkbutton(
    root, text="Code Runner (C, C++, Java, JS)", variable=opt_b,
    font=('Segoe UI', 12),
    bg="#2E2E2E", fg="white",
    activebackground="#2E2E2E", activeforeground="white",
    selectcolor="#2E2E2E"
).pack(anchor='w', padx=30)

tk.Checkbutton(
    root, text="Python Extension", variable=opt_c,
    font=('Segoe UI', 12),
    bg="#2E2E2E", fg="white",
    activebackground="#2E2E2E", activeforeground="white",
    selectcolor="#2E2E2E"
).pack(anchor='w', padx=30)

tk.Button(
    root, text="Download & Install", command=run_install_thread,
    font=('Segoe UI', 12, "bold"),
    bg="#4CAF50", fg="white",
    activebackground="#45A049"
).pack(pady=20, ipadx=10, ipady=5)

root.mainloop()
