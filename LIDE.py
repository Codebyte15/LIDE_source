import os, re, sys, time, zipfile, ctypes, threading, subprocess, webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk
import requests
import customtkinter as ctk
import tkinter as tk
import importlib

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class ide:
    def __init__(self):
        self.root = ctk.CTk()
        try:
            self.root.wm_iconbitmap("icon/lide.ico")
        except Exception:
            pass
        self.VERSION = "v2.2.0_pre-release"
        self.BASE_URL = "https://github.com/Codebyte15/Lide_Code/releases/download"
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")
        self.root.after(100, lambda:self.root.state("zoomed"))
        self.root.minsize(500, 500)
        self.root.maxsize(5000, 5000)
        self.root.title("LIDE - (Lightweight Internal Development Editor) v2.2.0")
        self.menubar = None
        self.editor_frame = None
        self.current_file = None
        self.is_saved = True
        self.zoom = int(18)
        self.appdata = os.getenv("APPDATA")
        self.settings_path = os.path.join(self.appdata, "LIDE", "Settings.ini")
        os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
        open(self.settings_path, "a").close()
        self.file_name = os.path.join(self.appdata, "LIDE", "saved_filename.ini")
        os.makedirs(os.path.dirname(self.file_name), exist_ok=True)
        open(self.file_name, "a").close()
        self.project_appdata = os.path.join(self.appdata, "LIDE","Project")
        os.makedirs(os.path.dirname(self.project_appdata), exist_ok=True)
        self.project_appdata_project_file = os.path.join(self.project_appdata, "Project.ini")
        os.makedirs(os.path.dirname(self.project_appdata_project_file), exist_ok=True)
        open(self.project_appdata_project_file, "a").close()
        self.zoom_in_appdata = os.path.join(self.appdata, "LIDE", "zoom.ini")
        os.makedirs(os.path.dirname(self.zoom_in_appdata), exist_ok=True)
        open(self.zoom_in_appdata, "a").close()

        if os.path.exists(self.file_name):
            with open(self.file_name, "r") as f:
                self.last_file = f.read().strip()
                if self.last_file and os.path.exists(self.last_file):
                    self.current_file = self.last_file
            
        if os.path.exists(self.zoom_in_appdata):
            with open(self.zoom_in_appdata, "r") as f:
                self.zoom_read = f.read().strip()
                try:
                    self.zoom = int(self.zoom_read)
                except ValueError:
                    self.zoom = 17
                
        if os.path.exists(self.project_appdata_project_file):
            try: 
                with open(self.project_appdata_project_file, "r") as f:
                    lines = f.readlines()
                self.firstline  = lines[0].strip() if len(lines) > 0 else ""
                self.secondline = lines[1].strip() if len(lines) > 1 else ""
                self.thirdline  = lines[2].strip() if len(lines) > 2 else ""
                self.fourthline = lines[3].strip() if len(lines) > 3 else ""
            except Exception:
                pass
        else:
            self.zoom = 17
            self.firstline = ""
            self.secondline = ""
            self.thirdline = ""
            self.fourthline = ""
        self.file_menu = None
        self.preferences_menu = None
        self.run_menu = None
        self.debug_menu = None
        self.plugin_menu = None
        self.help_menu = None
        self.editor = None
        self.decompile_editor = None
        self.preview_editor = None
        self.line_count_label = None
        self.character_label = None
        self.line_numbers = None
        self.scrollbar = None
        self.separator = None
        self.project = None
        self.project_name = self.firstline or None
        self.project_location = self.secondline or None
        self.version = self.thirdline or None
        self.project_description = self.fourthline or None
                
        self.BLOCK_KEYWORDS = {
            ".py":  ('def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally', 'with', 'async','{','[','('),
            ".c":   ('if', 'else', 'for', 'while', 'do', 'switch', 'case', 'struct', 'union', 'enum', 'goto','{','[','('),
            ".cpp": ('if', 'else', 'for', 'while', 'do', 'switch', 'case', 'struct', 'union', 'enum', 'class', 'try', 'catch','{','[','('),
            ".java":('if', 'else', 'for', 'while', 'do', 'switch', 'case', 'try', 'catch', 'finally', 'class', 'interface', 'enum','{','[','('),
            ".js":  ('if', 'else', 'for', 'while', 'do', 'switch', 'case', 'function', 'class', 'try', 'catch', 'finally','{','[','(')
        }

        self.HIGHLIGHT_RULES = {
            ".py": {
                "keywords": (
                    "def", "class", "if", "elif", "else", "for", "while", "try", "except",
                    "finally", "with", "import", "from", "return", "as", "pass", "raise",
                    "lambda", "yield", "global", "nonlocal", "assert", "del", "in", "is",
                    "not", "and", "or", "break", "continue"
                ),
                "datatypes": ("int", "float", "str", "bool", "list", "dict", "set", "tuple"),
                "builtins": ("print", "len", "range", "open", "super", "self"),
                "booleans": ("True", "False", "None"),
                "colors": {
                    "keyword": "#569CD6",
                    "datatype": "#4FC1FF",
                    "builtin": "#4EC9B0",
                    "boolean": "#569CD6",
                    "string": "#CE9178",
                    "comment": "#6A9955",
                    "number": "#B5CEA8",
                    "operator": "#D4D4D4",
                    "decorator": "#C586C0",
                    "class": "#4EC9B0",
                    "function": "#DCDCAA"
                }
            },

            ".c": {
                "keywords": ("if", "else", "for", "while", "return", "switch", "case", "break", "continue","include", "define", "typedef", "struct", "union", "enum"),
                "datatypes": ("int", "float", "double", "char", "void", "short", "long", "unsigned", "signed", "bool"),
                "booleans": ("true", "false"),
                "colors": {
                    "keyword": "#569CD6",
                    "datatype": "#4FC1FF",
                    "boolean": "#569CD6",
                    "string": "#CE9178",
                    "comment": "#6A9955",
                    "number": "#B5CEA8",
                    "operator": "#D4D4D4",
                    "function": "#DCDCAA"
                }
            },

            ".cpp": {
                "keywords": ("if", "else", "for", "while", "return", "switch", "case", "break", "continue", "try", "catch", "namespace", "using", "new", "delete","include", "define", "typedef", "struct", "union", "enum", "class"),
                "datatypes": ("int", "float", "double", "char", "void", "short", "long", "unsigned", "signed", "bool", "class", "struct"),
                "booleans": ("true", "false"),
                "preprocessor": ("#include", "#define", "#ifdef", "#ifndef", "#endif"),
                "colors": {
                    "keyword": "#569CD6",
                    "datatype": "#4FC1FF",
                    "boolean": "#569CD6",
                    "string": "#CE9178",
                    "comment": "#6A9955",
                    "number": "#B5CEA8",
                    "operator": "#D4D4D4",
                    "preprocessor": "#C586C0",
                    "class": "#4EC9B0",
                    "function": "#DCDCAA"
                }
            },

            ".java": {
                "keywords": ("class", "public", "private", "protected", "static", "final", "abstract", "try", "catch", "finally", "return", "new", "this", "extends", "implements", "throw", "throws"),
                "datatypes": ("int", "float", "double", "char", "boolean", "long", "void", "byte", "short", "String"),
                "booleans": ("true", "false", "null"),
                "colors": {
                    "keyword": "#569CD6",
                    "datatype": "#4FC1FF",
                "boolean": "#569CD6",
                    "string": "#CE9178",
                    "comment": "#6A9955",
                    "number": "#B5CEA8",
                    "operator": "#D4D4D4",
                    "class": "#4EC9B0",
                    "function": "#DCDCAA"
                }
            },

            ".js": {
                "keywords": ("function", "var", "let", "const", "if", "else", "for", "while", "return", "try", "catch", "finally", "class", "export", "import", "extends", "new", "throw", "await", "async"),
                "datatypes": ("Number", "String", "Boolean", "Array", "Object", "Symbol", "BigInt"),
                "booleans": ("true", "false", "null", "undefined"),
                "colors": {
                    "keyword": "#569CD6",
                    "datatype": "#4FC1FF",
                    "boolean": "#569CD6",
                    "string": "#CE9178",
                    "comment": "#6A9955",
                    "number": "#B5CEA8",
                    "operator": "#D4D4D4",
                    "class": "#4EC9B0",
                    "function": "#DCDCAA"
                }
            }
        }
    
    def update_download(self,latest_tag):
        url = "https://github.com/Codebyte15/Lide_Code"
        timeout = 5 
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                print("Internet is working")
            else:
                messagebox.showinfo("Connection","Internet might be down (status code != 200)")
        except requests.ConnectionError:
            messagebox.showinfo("Connection","Internet is Not Working")
    
        try:
            url = f"{self.BASE_URL}/{latest_tag}/LIDE_{latest_tag}-setup.zip"
            downloads = Path.home() / "Downloads"
            zip_path = downloads / "LIDE_setup.zip"
            extract_dir = downloads / "LIDE_extracted"
            headers = {"User-Agent": "Mozilla/5.0"}
    
            with requests.get(url, stream=True, headers=headers) as r:
                r.raise_for_status()
                with open(zip_path, "wb") as f:
                    for chunk in r.iter_content(8192):
                        if chunk:
                            f.write(chunk)
    
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(extract_dir)
    
            for file in os.listdir(extract_dir):
                if file.lower().endswith(".exe"):
                    subprocess.Popen(os.path.join(extract_dir, file), shell=True)
                    break
        except Exception as e:
            print("Update failed:", e)

    def check_update(self):
        owner = "Codebyte15"
        repo = "Lide_Code"
        url = f"https://api.github.com/repos/{owner}/{repo}/tags"
    
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            tags = response.json()
            if not tags:
                return None
    
            latest_tag = tags[0]["name"]
    
            if self.VERSION != latest_tag:
                verify_update = messagebox.askyesno("Update", f"New version {latest_tag} available.\nDownload now?")
                if verify_update:
                    self.update_download(latest_tag)
                    IDE.root.after(500, lambda: IDE.root.quit())
                    return
                IDE.root.after(100, lambda:IDE.root.state("zoomed"))
            return latest_tag
    
        except Exception as e:
            print("Error checking update:", e)
            return None
            
    def main(self,root):
        if os.path.exists(self.settings_path):
            with open(self.settings_path, "r") as f:
                Color_mode = f.read().strip()
                self.Color_Mode(Color_mode)
        self.menubar = tk.Menu(root)
        self.root.config(menu=self.menubar)
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="New", command=self.new_file)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Create Project", command=self.Project)
        self.file_menu.add_command(label="Open Project", command=self.open_project)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_close)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.preferences_menu = tk.Menu(self.menubar, tearoff=0)
        self.preferences_menu.add_command(label="Dark Mode", command=lambda: self.Dark_Mode())
        self.preferences_menu.add_command(label="Preview", command=lambda: self.preview())
        self.menubar.add_cascade(label="Preferences", menu=self.preferences_menu)
        self.run_menu = tk.Menu(self.menubar, tearoff=0)
        self.run_menu.add_command(label="CMD", command=lambda: self.run_app("CMD"))
        self.menubar.add_cascade(label="Run", menu=self.run_menu)
        self.debug_menu = tk.Menu(self.menubar, tearoff=0)
        self.debug_menu.add_command(label="Decompile program to hex", command=lambda: self.decompile_app())
        self.menubar.add_cascade(label="Decompile", menu=self.debug_menu)
        self.plugin_menu = tk.Menu(self.menubar, tearoff=0)
        self.plugin_menu.add_command(label="Download Plugins", command=lambda: self.download_plugin())
        self.plugin_menu.add_command(label="Make Plugins", command=lambda: self.Make_plugin())
        self.menubar.add_cascade(label="Plugins", menu=self.plugin_menu)
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.help_menu.add_command(label="About", command=self.About_section)
        self.help_menu.add_command(label="Show Shortcuts", command=self.Shortcuts_section)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)
        self.editor_frame = ctk.CTkFrame(root, fg_color=self.bg_color)
        self.editor_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1) 
        self.scrollbar = ctk.CTkScrollbar(self.editor_frame, orientation="vertical", fg_color=self.line_num)
        self.scrollbar.pack(side="right", fill="y")
        self.line_numbers = ctk.CTkTextbox(
            self.editor_frame,
            width=50,
            fg_color=self.line_num,
            text_color=self.line_num_fg,
            font=("Consolas", self.zoom),
            corner_radius=0,
            border_width=0,
            wrap="none",
            state="disabled",
            activate_scrollbars=False
        )
        self.line_numbers.pack(side="left", fill="y")

        self.editor = ctk.CTkTextbox(
            self.editor_frame,
            font=("Consolas", self.zoom),
            fg_color=self.color,
            text_color=self.fg_color,
            corner_radius=0,
            border_width=0,
            wrap="none",
            undo=True,
            activate_scrollbars=False,
            yscrollcommand=self.scrollbar.set
        )
        self.editor.pack(side="left", fill="both", expand=True)
        
        def on_scrollbar(*args):
            self.editor.yview(*args)
            self.line_numbers.yview(*args)

        self.scrollbar.configure(command=on_scrollbar)
        def on_editor_mousewheel(event):
            global zoom
            ctrl_pressed = (event.state & 0x4) != 0 
            if ctrl_pressed:
                if hasattr(event, 'delta'):
                    self.zoom += 1 if event.delta > 0 else -1
                else:
                    if event.num == 4:
                        zoom += 1
                    elif event.num == 5:
                        zoom -= 1

                self.zoom = max(5, min(self.zoom, 70))
                with open(self.zoom_in_appdata, "w") as f:
                    f.write(str(self.zoom))

                self.editor.configure(font=("Consolas", self.zoom))
                if self.line_numbers:
                    self.line_numbers.configure(font=("Consolas", self.zoom))
                self.update_line_numbers()
                return "break"
            else:
                if hasattr(event, 'delta'):
                    scroll_units = int(-1 * (event.delta / 120))
                    self.editor.yview_scroll(scroll_units, "units")
                    self.line_numbers.yview_scroll(scroll_units, "units")
                else:
                    if event.num == 4:
                        self.editor.yview_scroll(-1, "units")
                        self.line_numbers.yview_scroll(-1, "units")
                    elif event.num == 5:
                        self.editor.yview_scroll(1, "units")
                        self.line_numbers.yview_scroll(1, "units")
        
                editor_fraction = self.editor.yview()
                self.scrollbar.set(editor_fraction[0], editor_fraction[1])
                return "break"
        
        self.editor.bind("<MouseWheel>", on_editor_mousewheel)
        self.editor.bind("<Button-4>", on_editor_mousewheel)
        self.editor.bind("<Button-5>", on_editor_mousewheel)
        self.line_count_label = ctk.CTkLabel(master=root, text="lines = 0",font=("Cascadia Mono Light", 12), text_color=self.fg_color)
        self.line_count_label.grid(row=1, column=0, sticky="w", padx=(150,0), pady=2)
        self.character_label = ctk.CTkLabel(root, text="length - 0",font=("Cascadia Mono Light", 12), text_color=self.fg_color)
        self.character_label.grid(row=1, column=0, sticky="w", padx=(50,0), pady=2)
        root.configure(fg_color=self.bg_color)
        if self.current_file:
            try:
                with open(self.current_file, "r", encoding="utf-8") as f:
                    self.editor.insert("1.0", f.read())
                self.update_line_count()
                self.update_title()
                self.highlight_syntax()
                self.update_line_numbers()
            except Exception:
                pass

    def preview(self):
        if self.preview_editor and self.preview_editor.winfo_ismapped():
            self.preview_editor.grid_forget()
            self.preview_editor = None
            return
        self.preview_editor = ctk.CTkTextbox(master=self.root,font=("Consolas",5),fg_color=self.color,text_color=self.fg_color,corner_radius=0,border_width=0,state="disabled")
        self.preview_editor.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.root.grid_columnconfigure(1, weight=0)
        self.preview_editor.configure(state="disabled")
        self.update_preview_content()

    def update_preview_content(self):
        if self.preview_editor:
            content = self.editor.get("1.0", "end-1c")
            self.preview_editor.configure(state="normal")
            self.preview_editor.delete("1.0", "end")
            self.preview_editor.insert("1.0", content)
            self.preview_editor.configure(state="disabled")
            self.update_line_count(content)

    def update_line_count(self,content=None,char_count=None):
        if content is None:
            content = self.editor.get("1.0", "end-1c")
        if char_count is None:
            char_count = len(content)
        lines = [line for line in content.split("\n") if line.strip()]
        self.line_count_label.configure(text=f"lines = {len(lines)}")
        self.character_label.configure(text=f"length = {char_count}")
        
    def update_line_numbers(self,event=None):
        if not self.line_numbers or not self.editor:
            return
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", "end")
        total_lines = int(self.editor.index('end-1c').split('.')[0])
        line_numbers_text = "\n".join(str(i) for i in range(1, total_lines + 1))
        self.line_numbers.insert("1.0", line_numbers_text)
        self.line_numbers.configure(state="disabled")    

    def new_file(self):
        global current_file, is_saved
        name = simpledialog.askstring("Input", "Enter file name with extension:")
        if not name:
            return
        folder = filedialog.askdirectory(title="Select folder to save file")
        if not folder:
            return
        self.current_file = os.path.join(folder, name)
        open(self.current_file, "w").close()
        content = self.editor.get("1.0", "end-1c")
        self.editor.delete("1.0", "end")
        self.highlight_syntax()
        self.is_saved = True
        with open(self.file_name, "w") as f:
            f.write(self.current_file)
        self.update_title()
        self.update_preview_content()
        
    def open_file(self):
        path = filedialog.askopenfilename(title="Select a file",filetypes=(("All files", "*.*"),))
        if not path:
            return
        data_size = os.path.getsize(path) 
        if data_size >= 20971520:
            messagebox.showinfo("Large File", "The file is too large")
            return
        self.current_file = path
        extension = Path(self.current_file).suffix
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", "Loading large file, please wait...\n")
        self.editor.update_idletasks()
        def load_large_file():
            try:
                chunk_size = 8192
                content_chunks = []
                with open(self.current_file, "r", encoding="utf-8", errors="ignore") as f:
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        content_chunks.append(chunk)
                content = ''.join(content_chunks)
                def insert_content():
                    global is_saved
                    self.editor.delete("1.0", "end")
                    self.editor.insert("1.0", content)
                    self.highlight_syntax()
                    self.update_line_count()
                    self.update_line_numbers()
                    self.update_title()
                    with open(self.file_name, "w", encoding="utf-8") as f:
                        f.write(self.current_file)
                    self.is_saved = True
                self.root.after(0, insert_content)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load file:\n{e}"))
        threading.Thread(target=load_large_file, daemon=True).start()
        
    def save_file(self,event=None):
        global is_saved, extension
        if os.path.exists(os.path.dirname(self.settings_path)) or os.path.dirname(self.settings_path):
            with open(self.settings_path, "w") as f:
                f.write(self.Colorbutton)
        if not self.current_file:
            return
        with open(self.current_file, "w", encoding="utf-8") as f:
            f.write(self.editor.get("1.0", "end-1c"))
            extension = Path(self.current_file).suffix
        self.is_saved = True
        with open(self.file_name, "w") as f:
            f.write(self.current_file)
        self.update_title()
        return "break"

    def Project(self):
        if self.project_name:
            self.open_project()
            return

        if getattr(self, 'project', None):
            try:
                self.project.destroy()
            except Exception:
                pass

        self.project = ctk.CTk()
        self.project.attributes('-topmost', True)
        try:
            self.project.wm_iconbitmap("icon/lide.ico")
        except Exception:
            pass
        self.project.resizable(False, False)
        self.project.geometry("600x500")
        self.project.title("Project Setup")
        self.project.grid_columnconfigure(0, weight=1)
        self.project.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        self.project_name_entry = ctk.CTkEntry(self.project, placeholder_text="Project Name", width=400, height=40)
        self.project_name_entry.grid(row=0, column=0, pady=(10, 2), padx=20)

        location_frame = ctk.CTkFrame(self.project)
        location_frame.grid(row=1, column=0, pady=(2, 2), padx=(30, 0))

        location_entry = ctk.CTkEntry(location_frame, placeholder_text="Project Location (existing folder)", width=300, height=40)
        location_entry.pack(side="left", padx=(0, 5))

        version_entry = ctk.CTkEntry(self.project, placeholder_text="Version Number", width=400, height=40)
        version_entry.grid(row=2, column=0, pady=(2, 2), padx=20)

        project_description_entry = ctk.CTkEntry(self.project, placeholder_text="Project Description", width=400, height=40)
        project_description_entry.grid(row=3, column=0, pady=(2, 2), padx=20)

        def browse_location():
            self.project.attributes('-topmost', False)
            folder_selected = filedialog.askdirectory(title="Select an empty folder")
            self.project.attributes('-topmost', True)
            if not folder_selected:
                return
            if os.listdir(folder_selected):
                messagebox.showerror("Invalid Selection", "Please select an empty folder.")
                return
            location_entry.delete(0, ctk.END)
            location_entry.insert(0, folder_selected)

        browse_button = ctk.CTkButton(location_frame, text="Select an Empty Folder", width=80, command=browse_location)
        browse_button.pack(side="left")

        def create_project_callback():
            self.project_name = self.project_name_entry.get().strip()
            self.project_location = location_entry.get().strip()
            self.version = version_entry.get().strip()
            self.project_description = project_description_entry.get().strip()

            if not self.project_name or not self.project_location or not self.version or not self.project_description:
                messagebox.showerror("Error", "All fields must be filled.")
                return

            if not os.path.exists(self.project_location):
                messagebox.showerror("Error", "The specified Project Location does not exist.")
                return

            project_file = os.path.join(self.project_location, "Project_Config.ini")
            project_details = f"{self.project_name}\n{self.project_location}\n{self.version}\n{self.project_description}\n"
            with open(project_file, "w") as f:
                f.write(project_details)
            with open(self.project_appdata_project_file, "w") as f:
                f.write(project_details)

            folders = ["lib/lib.txt", "assets/assests.txt", "src/src.txt", "tests/tests.txt", 
                       "docs/docs.txt", "extensions/extensions.txt"]
            for path in folders:
                full_path = os.path.join(self.project_location, path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

            files = ["gitignore.md", "README.md", "requirements.txt", "LICENSE.md"]
            for file in files:
                open(os.path.join(self.project_location, file), "a").close()

            messagebox.showinfo("Success", f"Project '{self.project_name}' created successfully!")
            self.open_project()

        create_project = ctk.CTkButton(self.project, text="Create Project", font=('Arial', 15), command=create_project_callback)
        create_project.grid(row=4, column=0, pady=(10, 10))

        self.project.mainloop()

    def open_project(self):
        if getattr(self, 'project', None):
            try:
                self.project.destroy()
            except Exception:
                pass

        if not self.project_location:
            messagebox.showwarning("Error", "No Project is currently loaded")
            return

        if not os.path.exists(self.project_location):
            messagebox.showwarning("Error", "The Project Location Doesn't Exist Anymore\nIt might have been deleted")
            self.project_name = None
            self.project_location = None
            self.version = None
            self.project_description = None
            with open(self.project_appdata_project_file, "w") as f:
                f.write("")
            return

        self.project = ctk.CTk()
        self.project.attributes('-topmost', True)
        try:
            self.project.wm_iconbitmap("icon/lide.ico")
        except Exception:
            pass

        def open_file():
            global current_file, is_saved, extension
            self.project.attributes('-topmost', False)
            path = filedialog.askopenfilename(initialdir=self.project_location, title="Select a file", filetypes=(("All files", "*.*"),))
            if not path:
                return
            current_file = path
            extension = Path(current_file).suffix
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", "Loading large file, please wait...\n")
            self.editor.update_idletasks()

            def load_large_file():
                try:
                    chunk_size = 8192
                    content_chunks = []
                    with open(current_file, "r", encoding="utf-8", errors="ignore") as f:
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            content_chunks.append(chunk)
                    content = ''.join(content_chunks)

                    def insert_content():
                        global is_saved
                        self.editor.delete("1.0", "end")
                        self.editor.insert("1.0", content)
                        self.highlight_syntax()
                        self.update_line_count()
                        self.update_title()
                        with open(self.file_name, "w", encoding="utf-8") as f:
                            f.write(current_file)
                        is_saved = True

                    self.root.after(0, insert_content)

                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load file:\n{e}"))

            threading.Thread(target=load_large_file, daemon=True).start()
            if self.project:
                self.project.destroy()

        def new():
            global current_file, is_saved
            self.project.attributes('-topmost', False)
            name = simpledialog.askstring("Input", "Enter file name with extension:")
            if not name:
                return
            folder = filedialog.askdirectory(initialdir=self.project_location, title="Select folder to save file")
            if not folder:
                return
            self.current_file = os.path.join(folder, name)
            open(self.current_file, "w").close()
            content = self.editor.get("1.0", "end-1c")
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", content)
            self.highlight_syntax()
            is_saved = True
            with open(self.file_name, "w") as f:
                f.write(self.current_file)
            self.update_title()
            if self.project:
                self.project.destroy()
            self.update_preview_content()

        def delete():
            with open(self.project_appdata_project_file, "w") as f:
                f.write("")
            self.project.attributes('-topmost', False)
            answer = messagebox.askyesno("Confirm delete", "Are you sure you want to delete this project?")
            if answer:
                delete_path = os.path.join(self.project_location, "Project_Config.ini")
                if os.path.exists(delete_path):
                    os.remove(delete_path)
                self.project_name = None
                self.project_location = None
                self.version = None
                self.project_description = None
                if getattr(self, 'project', None):
                    try:
                        self.project.destroy()
                    except Exception:
                        pass
            else:
                self.project.attributes('-topmost', True)
                
        self.project.resizable(False, False)
        self.project.geometry("600x500")
        self.project.title(f"Project: {self.project_name}")

        if not self.project_name:
            messagebox.showwarning("Error", "No Project is currently loaded")
        else:
            ctk.CTkLabel(self.project, text=f"Project Name: {self.project_name}", font=("Arial", 20)).pack(pady=15)
            ctk.CTkLabel(self.project, text=f"Project Location: {self.project_location}", font=("Arial", 20)).pack(pady=15)
            ctk.CTkLabel(self.project, text=f"Project Version: {self.version}", font=("Arial", 20)).pack(pady=15)
            ctk.CTkLabel(self.project, text=f"Project Description: {self.project_description}", font=("Arial", 20)).pack(pady=15)

            ctk.CTkButton(self.project, text="New File in Project", font=("Arial", 15), command=new).pack(pady=15)
            ctk.CTkButton(self.project, text="Open File Project", font=("Arial", 15), command=open_file).pack(pady=15)
            ctk.CTkButton(self.project, text="Delete Project", font=("Arial", 15), command=delete).pack(pady=15)

        self.project.mainloop()

    def run_app(self,filetype):
        if not self.current_file:
            messagebox.showwarning("No File", "Create or open a file first!")
            return
        ext = os.path.splitext(self.current_file)[1].lower()
        self.save_file()
        if filetype == "CMD":
            path = os.path.dirname(self.current_file) or '.'
            subprocess.Popen("start cmd", shell=True, cwd=path)      
            
    def Dark_Mode(self):
        if self.color == "white":
            self.color = "gray10"
            self.fg_color = "white"
            self.bg_color = "gray15"
            self.Colorbutton = "Dark Mode"
            self.line_num = "gray5"
            self.line_num_fg = "white"
            ctk.set_appearance_mode("dark")
        else:
            self.color = "white"
            self.fg_color = "gray10"
            self.bg_color = "SystemButtonFace"
            self.Colorbutton = "Default Mode"
            self.line_num = "Ghost White"
            self.line_num_fg = "black"
            ctk.set_appearance_mode("light")

        os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
        with open(self.settings_path, "w") as f:
            f.write(self.Colorbutton)
    
        if self.editor:
            self.editor.configure(fg_color=self.color, text_color=self.fg_color)
        self.root.configure(fg_color=self.bg_color)
        if self.preview_editor:
            self.preview_editor.configure(fg_color=self.color, text_color=self.fg_color)
        if self.line_numbers:
            self.line_numbers.configure(fg_color=self.line_num, text_color=self.line_num_fg)
        if self.line_count_label:
            self.line_count_label.configure(text_color=self.fg_color)
        if self.character_label:
            self.character_label.configure(text_color=self.fg_color)
        if self.scrollbar:
            self.scrollbar.configure(fg_color=self.line_num)

    def Color_Mode(self,mode):
        global color, fg_color, bg_color, Colorbutton, line_num, line_num_fg
        if mode.lower() == "default mode":
            self.color = "white"
            self.fg_color = "gray10"
            self.bg_color = "SystemButtonFace"
            self.Colorbutton = "Default Mode"
            self.line_num = "Ghost White"
            self.line_num_fg = "black"
            ctk.set_appearance_mode("light")
        else:
            self.color = "gray10"
            self.fg_color = "white"
            self.bg_color = "gray15"
            self.Colorbutton = "Dark Mode"
            self.line_num = "gray5"
            self.line_num_fg = "white"
            ctk.set_appearance_mode("dark")

        if self.editor:
            self.editor.configure(fg_color=self.color, text_color=self.fg_color)
        self.root.configure(fg_color=self.bg_color)
        if self.preview_editor:
            self.preview_editor.configure(fg_color=self.color, text_color=self.fg_color)
        if self.line_count_label:
            self.line_count_label.configure(text_color=self.fg_color)
        if self.character_label:
            self.character_label.configure(text_color=self.fg_color)
        if self.line_numbers:
            self.line_numbers.configure(fg_color=self.line_num, text_color=self.line_num_fg)
        if self.scrollbar:
            self.scrollbar.configure(fg_color=self.line_num)
    
    def decompile_app(self):
        data = filedialog.askopenfilename(
            title="Select the file",
            filetypes=(("Executable files", "*.exe"), ("All files", "*.*")),
        )
        if not data:
            return
        data_size = os.path.getsize(data) 
        if data_size >= 20971520:
            messagebox.showinfo("Large File", "The file is too large")
            return
        try:
            with open(data, "rb") as f:
                binary_data = f.read()
            hex_data = binary_data.hex(" ").upper()
            bytes_list = hex_data.split()
            formatted = "\n".join(
                " ".join(bytes_list[i:i + 16]) for i in range(0, len(bytes_list), 16)
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read the file: {e}")
            return
        if self.decompile_editor is not None:
            try:
                self.decompile_editor.destroy()
            except:
                pass
            self.decompile_editor = None      
        self.decompile_editor = tk.Tk()
        self.decompile_editor.configure(bg="gray15")
        self.decompile_editor.attributes('-topmost', True)
        try:
            self.decompile_editor.wm_iconbitmap("icon/lide.ico")
        except Exception:
            pass
        self.decompile_editor.resizable(False, False)
        self.decompile_editor.geometry("600x500")
        self.decompile_editor.title(data)
        text_decompile = tk.Text(
            self.decompile_editor,
            font=("Consolas", 12),
            bg="gray15",
            fg ="white",
            wrap="none"
        )
        text_decompile.insert("0.0", formatted)
        text_decompile.pack(fill="both", expand=True)
        self.decompile_editor.mainloop()
        
    def download_plugin(self):
        check = messagebox.askyesno(
            "Plugin Updater",
            "This will open the Plugin Updater to download plugins.\nDo you want to continue?"
        )
        if not check:
            messagebox.showinfo("Cancelled", "Plugin download was cancelled.")
            return

        base_path = Path(sys.argv[0]).parent.resolve()
        exe_path = base_path / "updates" / "updater.exe"

        if exe_path.exists():
            try:
                subprocess.Popen([str(exe_path)], shell=True)
                self.on_close_without_prompt()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to launch updater:\n{e}")
            return

        messagebox.showerror("Error", f"Updater not found:\n{exe_path}")

    def Make_plugin(self):
        with open("Create_Plugins.txt", "r", encoding="utf-8") as f:
            plugin_txt = f.read()
        plugin_root = tk.Tk()
        plugin_root.geometry("700x600")
        plugin_root.title("Make Plugins")
        try:
            plugin_root.iconbitmap("icon/lide.ico")
        except Exception:
            pass
        plugin_root.resizable(False, False)
        plugin_txt_area = tk.Text(plugin_root,font=('Arial',10),fg=self.fg_color,bg=self.bg_color)
        plugin_txt_area.pack(expand=True, fill='both')
        plugin_txt_area.insert("1.0", plugin_txt)
        plugin_txt_area.config(state="disabled")
        plugin_root.mainloop()
    
    def plugin(self):
        loading_window = tk.Toplevel(self.root)
        loading_window.title("Loading")
        screen_width = loading_window.winfo_screenwidth()
        screen_height = loading_window.winfo_screenheight()
        x = (screen_width // 2) - (300 // 2)
        y = (screen_height // 2) - (100 // 2)
        loading_window.geometry(f"{300}x{100}+{x}+{y}")
        loading_window.geometry("300x100")
        loading_window.configure(bg="gray15")
        loading_window.attributes('-topmost', True)
        status_label = tk.Label(loading_window, text="Starting plugins... Please wait.",bg="gray15",fg="white")
        try:
            loading_window.iconbitmap("icon/lide.ico")
        except Exception as r:
            print("Icon Not Loaded")
        status_label.pack(expand=True, pady=20)
        loading_window.update()

        script_dir = Path(__file__).resolve().parent
        plugin_folder = script_dir / "plugins"
        loaded_plugins = {}

        if os.path.exists(plugin_folder):
            for folder in plugin_folder.iterdir():
                if folder.is_dir():
                    plugin_file = folder / f"{folder.name}.py"
                    if plugin_file.exists():
                        module_name = f"plugins.{folder.name}.{folder.name}"
    
                        try:
                            status_label.config(text=f"Loading plugin: {folder.name}")
                            loading_window.update()
    
                            module = importlib.import_module(module_name)
                            loaded_plugins[folder.name] = module
    
                            if hasattr(module, "setup_plugin"):
                                module.setup_plugin(self)
                                self.plugin_menu.add_command(label=folder.name)
    
                            time.sleep(0.3)
    
                        except Exception as e:
                            messagebox.showerror("Plugin Load Error", f"Error loading plugin '{folder.name}':\n{e}")
    
        loading_window.destroy()
                        
    def update_title(self):
        name = IDE.current_file if IDE.current_file else "Untitled"
        if not IDE.is_saved:
            name = "*" + name
        IDE.root.title(f"{name} - LIDE(Lightweight Internal Development Editor) v2.2.0")

    def on_text_change(self,event=None):
        global is_saved
        try:
            if IDE.editor.edit_modified():
                IDE.is_saved = False
                self.update_title()
                IDE.editor.edit_modified(False)
        except Exception:
            IDE.is_saved = False
            self.update_title()
    
    def on_close(self):
        result = messagebox.askyesnocancel("Confirm Exit","Do you want to save before exiting?\nUnsaved changes will be lost.")
        if result is True:
            if IDE.settings_path and IDE.Colorbutton:
                os.makedirs(os.path.dirname(IDE.settings_path), exist_ok=True)
                with open(IDE.settings_path, "w", encoding="utf-8") as f:
                    f.write(IDE.Colorbutton)
            if IDE.current_file:
                with open(IDE.current_file, "w", encoding="utf-8") as f:
                    f.write(IDE.editor.get("1.0", "end-1c"))
                IDE.is_saved = True
                if IDE.file_name:
                    with open(IDE.file_name, "w", encoding="utf-8") as f:
                        f.write(IDE.current_file)
            if getattr(IDE, 'project', None):
                try:
                    IDE.project.destroy()
                except Exception:
                    pass
            IDE.root.destroy()
        elif result is False:
            IDE.root.destroy()
        
    def on_close_without_prompt(self):
        result = True
        if result is True:
            if IDE.settings_path and IDE.Colorbutton:
                os.makedirs(os.path.dirname(IDE.settings_path), exist_ok=True)
                with open(IDE.settings_path, "w", encoding="utf-8") as f:
                    f.write(IDE.Colorbutton)
            if IDE.current_file:
                with open(IDE.current_file, "w", encoding="utf-8") as f:
                    f.write(IDE.editor.get("1.0", "end-1c"))
                IDE.is_saved = True
                if IDE.file_name:
                    with open(IDE.file_name, "w", encoding="utf-8") as f:
                        f.write(IDE.current_file)
            if getattr(IDE, 'project', None):
                try:
                    IDE.project.destroy()
                except Exception:
                    pass
            IDE.root.destroy()
        elif result is False:
            IDE.root.destroy()

    def auto_indent(self,event=None):
        ext = os.path.splitext(IDE.current_file or "")[1].lower()
        keywords = IDE.BLOCK_KEYWORDS.get(ext, IDE.BLOCK_KEYWORDS[".py"])
        index = IDE.editor.index("insert")
        line_start = f"{index.split('.')[0]}.0"
        current_line = IDE.editor.get(line_start, f"{line_start} lineend")
        leading_spaces = len(current_line) - len(current_line.lstrip(' '))
        increase_indent = False
        stripped = current_line.strip()
    
        for kw in keywords:
            if ext == ".py":
                if stripped.startswith(kw) and stripped.endswith(':'):
                    increase_indent = True
                    break
            else:
                if stripped.startswith(kw) or stripped.endswith(kw):
                    increase_indent = True
                    break

        IDE.editor.insert("insert", "\n")
        spaces = ' ' * leading_spaces
        if increase_indent:
            spaces += ' ' * 4
        IDE.editor.insert("insert", spaces)
        return "break"

    def highlight_syntax(self,event=None):
        ext = os.path.splitext(IDE.current_file or "")[1].lower()
        rules = IDE.HIGHLIGHT_RULES.get(ext, IDE.HIGHLIGHT_RULES[".py"])
        colors = rules["colors"]
        editor = IDE.editor
        text = IDE.editor.get("1.0", "end-1c")
        IDE.editor.tag_delete(*list(colors.keys()))
        for tag, color in colors.items():
            IDE.editor.tag_config(tag, foreground=color)
        def apply(pattern, tag, flags=0):
            for match in re.finditer(pattern, text, flags):
                IDE.editor.tag_add(tag, f"1.0+{match.start()}c", f"1.0+{match.end()}c")
        if ext in (".py", ".js", ".java", ".c", ".cpp"):
            apply(r"#.*" if ext == ".py" else r"//.*", "comment")
            apply(r"/\*[\s\S]*?\*/", "comment", re.DOTALL)
        apply(r"(['\"]{3})([\s\S]*?)\1", "string", re.DOTALL)
        apply(r"(['\"])(?:(?=(\\?))\2.)*?\1", "string") 
        apply(r"\b\d+(\.\d+)?\b", "number")
        apply(r"[+\-*/%=<>!~&|^]+", "operator")
        if ext == ".py":
            apply(r"@\w+", "decorator")
        if ext in (".c", ".cpp"):
            for directive in rules.get("preprocessor", []):
                apply(rf"{directive}", "preprocessor")
        for token_type in ("keywords", "datatypes", "builtins", "booleans"):
            if token_type in rules:
                for word in rules[token_type]:
                    apply(rf"\b{re.escape(word)}\b", token_type[:-1])
        apply(r"class\s+([A-Za-z_]\w*)", "class")
        apply(r"def\s+([A-Za-z_]\w*)", "function") 
        apply(r"function\s+([A-Za-z_]\w*)", "function")  
        apply(r"(\w+)\s*\(", "function")
        if ext in (".c", ".cpp"):
            apply(r"[A-Za-z_]\w*\s+[A-Za-z_]\w*(?=\()", "function")

    def combined_key_release(self,event=None):
        self.highlight_syntax(event)
        self.update_line_count()
        self.update_preview_content()
        self.update_line_numbers()

    def About_section(self):
        messagebox.showinfo(
            "About",
            """LIDE is a Simple Text Editor

    In this new version, you will get:
    1) Auto Version Checker And Downloader
    2) Bug Fixes with More Tabs"""
        )
        return

    def Shortcuts_section(self):
        messagebox.showinfo(
            "Shortcuts",
            """Shortcuts are listed below
    1) SAVE FILE - CTRL + S
    2) NEW FILE - CTRL + N
    3) OPEN FILE - CTRL + O
    4) RUN - Python(F5) ,C (F6) ,C++ (F7) ,Java (F8) ,HTML (F9), CMD(F10)"""
        )
        return
    def on_editor_mousewheel(self,event):
        global zoom
    
        ctrl_pressed = (event.state & 0x4) != 0 
    
        if ctrl_pressed:
            if hasattr(event, 'delta'):
                IDE.zoom += 1 if event.delta > 0 else -1
            else:
                if event.num == 4:
                    IDE.zoom += 1
                elif event.num == 5:
                    IDE.zoom -= 1
    
            IDE.zoom = max(5, min(zoom, 70))
            with open(IDE.zoom_in_appdata, "w") as f:
                f.write(str(zoom))
    
            IDE.editor.configure(font=("Consolas", zoom))
            if IDE.ine_numbers:
                IDE.line_numbers.configure(font=("Consolas", zoom))
            IDE.update_line_numbers()
            return "break"
        else:
            if hasattr(event, 'delta'):
                scroll_units = int(-1 * (event.delta / 120))
                IDE.editor.yview_scroll(scroll_units, "units")
                IDE.line_numbers.yview_scroll(scroll_units, "units")
            else:
                if event.num == 4:
                    IDE.editor.yview_scroll(-1, "units")
                    IDE.line_numbers.yview_scroll(-1, "units")
                elif event.num == 5:
                    IDE.editor.yview_scroll(1, "units")
                    IDE.line_numbers.yview_scroll(1, "units")
    
            editor_fraction = IDE.editor.yview()
            IDE.scrollbar.set(editor_fraction[0], editor_fraction[1])
            return "break"

IDE = ide()
IDE.main(IDE.root)
IDE.plugin()
IDE.preview()
IDE.check_update()
IDE.root.bind("<Control-s>", lambda e: IDE.save_file())
IDE.root.bind("<Control-n>", lambda e: IDE.new_file())
IDE.root.bind("<Control-o>", lambda e: IDE.open_file())
IDE.editor.bind("<<Modified>>", IDE.on_text_change)
IDE.editor.bind("<KeyRelease>", IDE.combined_key_release)
IDE.editor.bind("<Button-1>", lambda e: IDE.update_line_numbers())
IDE.editor.bind("<Return>", lambda e: IDE.update_line_numbers())
IDE.editor.bind("<BackSpace>", lambda e: IDE.update_line_numbers())
IDE.editor.bind("<Configure>", lambda e: IDE.update_line_numbers())
IDE.editor.bind("<Return>", IDE.auto_indent)
IDE.editor.bind("<Control-z>", lambda e: IDE.editor.event_generate("<<Undo>>"))
IDE.editor.bind("<Control-y>", lambda e: IDE.editor.event_generate("<<Redo>>"))
IDE.root.protocol("WM_DELETE_WINDOW", IDE.on_close)
IDE.root.mainloop()
