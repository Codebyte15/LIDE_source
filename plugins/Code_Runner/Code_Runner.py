import os
import subprocess
import webbrowser
from tkinter import messagebox
import shutil

def setup_plugin(IDE):
    IDE.run_menu.add_command(label="Python File", command=lambda: Code_run(IDE, "Python"))
    IDE.run_menu.add_command(label="C File", command=lambda: Code_run(IDE, "C"))
    IDE.run_menu.add_command(label="C++ File)", command=lambda: Code_run(IDE, "CPP"))
    IDE.run_menu.add_command(label="Java File", command=lambda: Code_run(IDE, "Java"))
    IDE.run_menu.add_command(label="HTML File", command=lambda: Code_run(IDE, "HTML"))
    print("Code Runner Plugin Has Been Loaded")

def run_cmd(command, cwd=None, env=None):
    subprocess.Popen(f'start cmd /k "{command}"', shell=True, cwd=cwd, env=env)


def Code_run(IDE, filetype):
    IDE.save_file()
    current_file = IDE.current_file

    if not current_file:
        messagebox.showwarning("No File", "Create or open a file first!")
        return

    ext = os.path.splitext(current_file)[1].lower()
    path = os.path.dirname(current_file) or '.'

    if filetype == "Python":
        python_exe = shutil.which("python") or shutil.which("python3")
        if not python_exe:
            messagebox.showerror("Python Not Found", "Python is not installed or not added to PATH.")
            return

        env = os.environ.copy()
        env.pop("TCL_LIBRARY", None)
        env.pop("TK_LIBRARY", None)
        cmd = f'{python_exe} "{current_file}" & pause & exit'
        run_cmd(cmd, env=env)
        return

    if filetype == "C":
        exe = os.path.splitext(current_file)[0] + ".exe"
        cmd = f'gcc "{current_file}" -o "{exe}" && "{exe}" & pause & exit'
        run_cmd(cmd)
        return

    if filetype == "CPP":
        exe = os.path.splitext(current_file)[0] + ".exe"
        cmd = f'g++ "{current_file}" -o "{exe}" && "{exe}" & pause & exit'
        run_cmd(cmd)
        return

    if filetype == "Java":
        name = os.path.splitext(os.path.basename(current_file))[0]
        cmd = f'cd /d "{path}" && javac "{current_file}" && java {name} & pause & exit'
        run_cmd(cmd)
        return

    if filetype == "HTML":
        webbrowser.open(current_file)
        return
    messagebox.showwarning("Unsupported Filetype", f"Running '{filetype}' files is not supported.")
