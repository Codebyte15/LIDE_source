import tkinter as tk
import customtkinter as ctk
import io, sys
import threading
from functools import partial
import builtins as py_builtins

class PythonPlugin:
    def __init__(self):
        self.name = "python_extension"
        self.gui_keywords = ["pygame", "arcade", "pyglet", "kivy", "cocos2d", "panda3d", "ursina", "moderngl", "pyopengl",
            "tk.", "tkinter", "ctk.", "customtkinter", "Toplevel", "Label", "Button", "Entry",
            "PyQt4", "PyQt5", "PyQt6", "PySide", "PySide2", "PySide6", "QtWidgets", "QMainWindow",
            "wx.", "wxFrame", "wx.Panel", "wx.App",
            "DearPyGui", "dpg.", "dpg.add_window",
            "matplotlib", "plt.show", "FigureCanvas", "NavigationToolbar2",
            "tkinter.ttk", "PySimpleGUI", "guizero", "kivy.app", "kivy.uix", "PyGameZero", "pgzero", "pygcurse",
            "vtk", "vispy", "glfw", "opengl", "mayavi", "panda3d",
        ]

    def run_code(self, IDE, event=None):
        if not getattr(IDE, "current_file", ""):
            self._display_output(IDE, "Run Code will only work if any file is created")
            return
        code = IDE.editor.get("1.0", "end-1c")
        if not code.strip():
            self._display_output(IDE, "There is no code written")
            return

        gui_detected = any(x in code for x in self.gui_keywords)

        if gui_detected:
            self._execute_code_main_thread(IDE, code)
        else:
            threading.Thread(target=self._execute_code_thread, args=(IDE, code), daemon=True).start()

    def _execute_code_thread(self, IDE, code):
        output = io.StringIO()
        try:
            sys.stdout = output
            sys.stderr = output
            exec(code, {"IDE": IDE, "input": partial(self._gui_input, IDE)})
        except Exception as e:
            output.write(str(e))
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
        self._display_output(IDE, output.getvalue())

    def _execute_code_main_thread(self, IDE, code):
        output = io.StringIO()
        try:
            sys.stdout = output
            sys.stderr = output
            exec(code, {"IDE": IDE, "input": partial(self._gui_input, IDE)})
        except Exception as e:
            output.write(str(e))
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
        self._display_output(IDE, output.getvalue())

    def _gui_input(self, IDE, prompt=""):
        result = []
        event = threading.Event()

        def submit_input():
            result.append(input_box.get())
            popup.destroy()
            event.set()

        popup = ctk.CTkToplevel(IDE.root)
        popup.title("Input Required")
        tk.Label(popup, text=prompt).pack(pady=5)
        input_box = ctk.CTkEntry(popup)
        input_box.pack(pady=5)
        submit_btn = ctk.CTkButton(popup, text="Submit", command=submit_input)
        submit_btn.pack(pady=5)
        input_box.focus()
        popup.grab_set()

        event.wait()
        return result[0]

    def _display_output(self, IDE, text):
        def update_gui():
            file_path = IDE.current_file
            printed = f"{file_path}:- {text}"
            IDE.plugin_python.configure(state="normal")
            IDE.plugin_python.delete("1.0", "end-1c")
            IDE.plugin_python.insert("1.0", printed)
            IDE.plugin_python.configure(state="disabled")
            IDE.plugin_python.see("end")
        IDE.root.after(0, update_gui)

    def start_plugin(self, IDE):
        if getattr(IDE, "plugin_python", None) is None:
            IDE.plugin_python = ctk.CTkTextbox(
                IDE.root,
                font=("Consolas", 10),
                fg_color=IDE.color,
                text_color=IDE.fg_color,
                wrap="none",
                height=200,
                state='disabled'
            )
            IDE.plugin_python.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        if getattr(IDE, "run_code_button", None) is None:
            IDE.run_code_button = ctk.CTkButton(
                IDE.root,
                text="Run Code for Python (F5)",
                command=partial(self.run_code, IDE)
            )
            IDE.run_code_button.grid(row=3, column=0, sticky="w", padx=5, pady=(0,5))


def setup_plugin(IDE):
    plugin = PythonPlugin()
    IDE.root.after(100, lambda: IDE.root.state("zoomed"))
    print("Python Plugin Loaded")
    IDE.root.bind("<F5>", partial(plugin.run_code, IDE), add="+")
    plugin.start_plugin(IDE)
