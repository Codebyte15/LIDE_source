import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import subprocess, os, re
from pathlib import Path
import threading
import webbrowser

current_file = None
is_saved = True
zoom = int(18)
appdata = os.getenv("APPDATA")
settings_path = os.path.join(appdata, "LIDE", "Settings.ini")
os.makedirs(os.path.dirname(settings_path), exist_ok=True)
open(settings_path, "a").close()
file_name = os.path.join(appdata, "LIDE", "saved_filename.ini")
os.makedirs(os.path.dirname(file_name), exist_ok=True)
open(file_name, "a").close()
project_appdata = os.path.join(appdata, "LIDE","Project")
os.makedirs(os.path.dirname(project_appdata), exist_ok=True)
project_appdata_project_file = os.path.join(project_appdata, "Project.ini")
os.makedirs(os.path.dirname(project_appdata_project_file), exist_ok=True)
open(project_appdata_project_file, "a").close()
zoom_in_appdata = os.path.join(appdata, "LIDE", "zoom.ini")
os.makedirs(os.path.dirname(zoom_in_appdata), exist_ok=True)
open(zoom_in_appdata, "a").close()

if os.path.exists(file_name):
    with open(file_name, "r") as f:
        last_file = f.read().strip()
        if last_file and os.path.exists(last_file):
            current_file = last_file
            
if os.path.exists(zoom_in_appdata):
    with open(zoom_in_appdata, "r") as f:
        zoom_read = f.read().strip()
        try:
            zoom = int(zoom_read)
        except ValueError:
            zoom = 17
            
if os.path.exists(project_appdata_project_file):
    try: 
        with open(project_appdata_project_file, "r") as f:
            lines = f.readlines()
        firstline  = lines[0].strip() if len(lines) > 0 else ""
        secondline = lines[1].strip() if len(lines) > 1 else ""
        thirdline  = lines[2].strip() if len(lines) > 2 else ""
        fourthline = lines[3].strip() if len(lines) > 3 else ""
    except Exception:
        pass
else:
    zoom = 17
    firstline = ""
    secondline = ""
    thirdline = ""
    fourthline = ""
            
BLOCK_KEYWORDS = {
    ".py":  ('def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally', 'with', 'async','{','[','('),
    ".c":   ('if', 'else', 'for', 'while', 'do', 'switch', 'case', 'struct', 'union', 'enum', 'goto','{','[','('),
    ".cpp": ('if', 'else', 'for', 'while', 'do', 'switch', 'case', 'struct', 'union', 'enum', 'class', 'try', 'catch','{','[','('),
    ".java":('if', 'else', 'for', 'while', 'do', 'switch', 'case', 'try', 'catch', 'finally', 'class', 'interface', 'enum','{','[','('),
    ".js":  ('if', 'else', 'for', 'while', 'do', 'switch', 'case', 'function', 'class', 'try', 'catch', 'finally','{','[','(')
}

HIGHLIGHT_RULES = {
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

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
try:
    root.wm_iconbitmap("icon/lide.ico")
except Exception:
    pass
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")
root.after(100, lambda:root.state("zoomed"))
root.minsize(500, 500)
root.maxsize(5000, 5000)
root.title("LIDE - (Lightweight Internal Development Editor)")

class IDE:
    editor = None
    decompile_editor = None
    preview_editor = None
    line_count_label = None
    character_label = None
    line_numbers = None
    scrollbar = None
    separator = None
    project = None
    open_project = None
    if firstline is None:
        project_name = None
    project_name = firstline
    if secondline is None:
        project_location = None
    project_location = secondline
    if thirdline is None:
        version = None
    version = thirdline
    if fourthline is None:
        project_description = None
    project_description = fourthline
    
    @staticmethod
    def main():
        global color, fg_color, Colorbutton, line_num, line_num_fg
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                Color_mode = f.read().strip()
                IDE.Color_Mode(Color_mode)
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=IDE.new_file)
        file_menu.add_command(label="Open", command=IDE.open_file)
        file_menu.add_command(label="Save", command=IDE.save_file)
        file_menu.add_command(label="Create Project", command=IDE.Project)
        file_menu.add_command(label="Open Project", command=IDE.open_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=on_close)
        menubar.add_cascade(label="File", menu=file_menu)
        preferences_menu = tk.Menu(menubar, tearoff=0)
        preferences_menu.add_command(label="Dark Mode", command=lambda: IDE.Dark_Mode())
        preferences_menu.add_command(label="Preview", command=lambda: IDE.preview())
        menubar.add_cascade(label="Preferences", menu=preferences_menu)
        run_menu = tk.Menu(menubar, tearoff=0)
        run_menu.add_command(label="Python File (F5)", command=lambda: IDE.run_app("Python"))
        run_menu.add_command(label="C File (F6)", command=lambda: IDE.run_app("C"))
        run_menu.add_command(label="C++ File (F7)", command=lambda: IDE.run_app("CPP"))
        run_menu.add_command(label="Java File (F8)", command=lambda: IDE.run_app("Java"))
        run_menu.add_command(label="html File (F9)", command=lambda: IDE.run_app("html"))
        run_menu.add_command(label="CMD (F10)", command=lambda: IDE.run_app("CMD"))
        menubar.add_cascade(label="Run", menu=run_menu)
        debug_menu = tk.Menu(menubar, tearoff=0)
        debug_menu.add_command(label="Decompile program to hex", command=lambda: IDE.decompile_app())
        menubar.add_cascade(label="Decompile", menu=debug_menu)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=About_section)
        help_menu.add_command(label="Show Shortcuts", command=Shortcuts_section)
        menubar.add_cascade(label="Help", menu=help_menu)
        editor_frame = ctk.CTkFrame(root, fg_color=bg_color)
        editor_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1) 
        IDE.scrollbar = ctk.CTkScrollbar(editor_frame, orientation="vertical", fg_color=line_num)
        IDE.scrollbar.pack(side="right", fill="y")
        IDE.line_numbers = ctk.CTkTextbox(
            editor_frame,
            width=50,
            fg_color=line_num,
            text_color=line_num_fg,
            font=("Consolas", zoom),
            corner_radius=0,
            border_width=0,
            wrap="none",
            state="disabled",
            activate_scrollbars=False
        )
        IDE.line_numbers.pack(side="left", fill="y")

        IDE.editor = ctk.CTkTextbox(
            editor_frame,
            font=("Consolas", zoom),
            fg_color=color,
            text_color=fg_color,
            corner_radius=0,
            border_width=0,
            wrap="none",
            undo=True,
            activate_scrollbars=False,
            yscrollcommand=IDE.scrollbar.set
        )
        IDE.editor.pack(side="left", fill="both", expand=True)
        
        def on_scrollbar(*args):
            IDE.editor.yview(*args)
            IDE.line_numbers.yview(*args)

        IDE.scrollbar.configure(command=on_scrollbar)
        def on_editor_mousewheel(event):
            global zoom
            ctrl_pressed = (event.state & 0x4) != 0 
            if ctrl_pressed:
                if hasattr(event, 'delta'):
                    zoom += 1 if event.delta > 0 else -1
                else:
                    if event.num == 4:
                        zoom += 1
                    elif event.num == 5:
                        zoom -= 1

                zoom = max(5, min(zoom, 70))
                with open(zoom_in_appdata, "w") as f:
                    f.write(str(zoom))

                IDE.editor.configure(font=("Consolas", zoom))
                if IDE.line_numbers:
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
        
        IDE.editor.bind("<MouseWheel>", on_editor_mousewheel)
        IDE.editor.bind("<Button-4>", on_editor_mousewheel)
        IDE.editor.bind("<Button-5>", on_editor_mousewheel)
        IDE.line_count_label = ctk.CTkLabel(master=root, text="lines = 0",font=("Cascadia Mono Light", 12), text_color=fg_color)
        IDE.line_count_label.grid(row=1, column=0, sticky="w", padx=(150,0), pady=2)
        IDE.character_label = ctk.CTkLabel(root, text="length - 0",font=("Cascadia Mono Light", 12), text_color=fg_color)
        IDE.character_label.grid(row=1, column=0, sticky="w", padx=(50,0), pady=2)
        root.configure(fg_color=bg_color)
        if current_file:
            try:
                with open(current_file, "r", encoding="utf-8") as f:
                    IDE.editor.insert("1.0", f.read())
                IDE.update_line_count()
                update_title()
                highlight_syntax()
                IDE.update_line_numbers()
            except Exception:
                pass

    @staticmethod
    def on_key_release(event=None):
        IDE.update_line_count()
        IDE.update_preview_content()
        IDE.update_line_numbers()

    @staticmethod
    def preview():
        if IDE.preview_editor and IDE.preview_editor.winfo_ismapped():
            IDE.preview_editor.grid_forget()
            IDE.preview_editor = None
            return
        IDE.preview_editor = ctk.CTkTextbox(master=root,font=("Consolas",5),fg_color=color,text_color=fg_color,corner_radius=0,border_width=0,state="disabled")
        IDE.preview_editor.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        root.grid_columnconfigure(1, weight=0)
        IDE.preview_editor.configure(state="disabled")
        IDE.update_preview_content()

    @staticmethod
    def update_preview_content():
        if IDE.preview_editor:
            content = IDE.editor.get("1.0", "end-1c")
            IDE.preview_editor.configure(state="normal")
            IDE.preview_editor.delete("1.0", "end")
            IDE.preview_editor.insert("1.0", content)
            IDE.preview_editor.configure(state="disabled")
            IDE.update_line_count(content)

    @staticmethod
    def update_line_count(content=None,char_count=None):
        if content is None:
            content = IDE.editor.get("1.0", "end-1c")
        if char_count is None:
            char_count = len(content)
        lines = [line for line in content.split("\n") if line.strip()]
        IDE.line_count_label.configure(text=f"lines = {len(lines)}")
        IDE.character_label.configure(text=f"length = {char_count}")
        
    @staticmethod
    def update_line_numbers(event=None):
        if not IDE.line_numbers or not IDE.editor:
            return
        IDE.line_numbers.configure(state="normal")
        IDE.line_numbers.delete("1.0", "end")
        total_lines = int(IDE.editor.index('end-1c').split('.')[0])
        line_numbers_text = "\n".join(str(i) for i in range(1, total_lines + 1))
        IDE.line_numbers.insert("1.0", line_numbers_text)
        IDE.line_numbers.configure(state="disabled")    

    @staticmethod
    def new_file():
        global current_file, is_saved
        name = simpledialog.askstring("Input", "Enter file name with extension:")
        if not name:
            return
        folder = filedialog.askdirectory(title="Select folder to save file")
        if not folder:
            return
        current_file = os.path.join(folder, name)
        open(current_file, "w").close()
        content = IDE.editor.get("1.0", "end-1c")
        IDE.editor.delete("1.0", "end")
        highlight_syntax()
        is_saved = True
        with open(file_name, "w") as f:
            f.write(current_file)
        update_title()
        IDE.update_preview_content()
        
    @staticmethod
    def open_file():
        global current_file, is_saved, extension
        path = filedialog.askopenfilename(title="Select a file",filetypes=(("All files", "*.*"),))
        if not path:
            return
        current_file = path
        extension = Path(current_file).suffix
        IDE.editor.delete("1.0", "end")
        IDE.editor.insert("1.0", "Loading large file, please wait...\n")
        IDE.editor.update_idletasks()
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
                    IDE.editor.delete("1.0", "end")
                    IDE.editor.insert("1.0", content)
                    highlight_syntax()
                    IDE.update_line_count()
                    IDE.update_line_numbers()
                    update_title()
                    with open(file_name, "w", encoding="utf-8") as f:
                        f.write(current_file)
                    is_saved = True
                root.after(0, insert_content)
            except Exception as e:
                root.after(0, lambda: messagebox.showerror("Error", f"Failed to load file:\n{e}"))
        threading.Thread(target=load_large_file, daemon=True).start()
        
    @staticmethod
    def save_file(event=None):
        global is_saved, extension
        if os.path.exists(os.path.dirname(settings_path)) or os.path.dirname(settings_path):
            with open(settings_path, "w") as f:
                f.write(Colorbutton)
        if not current_file:
            IDE.new_file()
            return
        with open(current_file, "w", encoding="utf-8") as f:
            f.write(IDE.editor.get("1.0", "end-1c"))
            extension = Path(current_file).suffix
        is_saved = True
        with open(file_name, "w") as f:
            f.write(current_file)
        update_title()
        return "break"
    
    @staticmethod
    def Project():
        global project_location, project_file
        if IDE.project_name:
            IDE.open_project()
            return
        if getattr(IDE, 'project', None):
            try:
                IDE.project.destroy()
            except Exception:
                pass
        IDE.project = ctk.CTk()
        IDE.project.attributes('-topmost', True)
        try:
            IDE.project.wm_iconbitmap("icon/lide.ico")
        except Exception:
            pass
        IDE.project.resizable(False, False)
        IDE.project.geometry("600x500")
        IDE.project.title("Project Setup")
        IDE.project.grid_columnconfigure(0, weight=1)
        IDE.project.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        IDE.project_name_entry = ctk.CTkEntry(IDE.project, placeholder_text="Project Name", width=400, height=40)
        IDE.project_name_entry.grid(row=0, column=0, pady=(10, 2), padx=20)
        location_frame = ctk.CTkFrame(IDE.project)
        location_frame.grid(row=1, column=0, pady=(2, 2), padx=(30,0))
        location_entry = ctk.CTkEntry(location_frame, placeholder_text="Project Location (existing folder)", width=300, height=40)
        location_entry.pack(side="left", padx=(0, 5))
        def browse_location():
            IDE.project.attributes('-topmost', False)
            folder_selected = filedialog.askdirectory(title="Select an empty folder")
            IDE.project.attributes('-topmost', True)
            if not folder_selected:
                return
            if os.listdir(folder_selected):
                messagebox.showerror("Invalid Selection", "Please select an empty folder.")
                return
            location_entry.delete(0, ctk.END)
            location_entry.insert(0, folder_selected)
        browse_button = ctk.CTkButton(location_frame, text="Select an Empty Folder", width=80, command=browse_location)
        browse_button.pack(side="left")
        version_entry = ctk.CTkEntry(IDE.project, placeholder_text="Version Number", width=400, height=40)
        version_entry.grid(row=2, column=0, pady=(2, 2), padx=20)
        project_description_entry = ctk.CTkEntry(IDE.project, placeholder_text="Project Description", width=400, height=40)
        project_description_entry.grid(row=3, column=0, pady=(2, 2), padx=20)    
        def create_project_callback():         
            IDE.project_name = IDE.project_name_entry.get().strip()
            IDE.project_location = location_entry.get().strip()
            IDE.version = version_entry.get().strip()
            IDE.project_description = project_description_entry.get().strip()
            if not IDE.project_name or not IDE.project_location or not IDE.version or not IDE.project_description:
                messagebox.showerror("Error", "All fields must be filled.")
                return
            if not os.path.exists(IDE.project_location):
                messagebox.showerror("Error", "The specified Project Location does not exist.")
                return
            project_file = os.path.join(IDE.project_location, "Project_Config.ini")
            project_details = (f"{IDE.project_name}\n{IDE.project_location}\n{IDE.version}\n{IDE.project_description}\n")
            with open(project_file, "w") as f:
                f.write(project_details)
            with open(project_appdata_project_file, "w") as f:
                f.write(project_details)
            project_file_built_in1 = os.path.join(IDE.project_location, "lib","lib.txt")
            os.makedirs(os.path.dirname(project_file_built_in1), exist_ok=True)
            project_file_built_in2 = os.path.join(IDE.project_location, "assets","assests.txt")
            os.makedirs(os.path.dirname(project_file_built_in2), exist_ok=True)
            project_file_built_in3 = os.path.join(IDE.project_location, "src","src.txt")
            os.makedirs(os.path.dirname(project_file_built_in3), exist_ok=True)
            project_file_built_in4 = os.path.join(IDE.project_location, "tests","tests.txt")
            os.makedirs(os.path.dirname(project_file_built_in4), exist_ok=True)
            project_file_built_in5 = os.path.join(IDE.project_location, "docs","docs.txt")
            os.makedirs(os.path.dirname(project_file_built_in5), exist_ok=True)
            project_file_built_in6 = os.path.join(IDE.project_location, "extensions","extensions.txt")
            os.makedirs(os.path.dirname(project_file_built_in6), exist_ok=True)
            project_file_built_in7 = os.path.join(IDE.project_location, "gitignore.md")
            open(project_file_built_in7, "a").close()
            project_file_built_in8 = os.path.join(IDE.project_location, "README.md")
            open(project_file_built_in8, "a").close()
            project_file_built_in9 = os.path.join(IDE.project_location, "requirements.txt")
            open(project_file_built_in9, "a").close()
            project_file_built_in10 = os.path.join(IDE.project_location, "LICENSE.md")
            open(project_file_built_in10, "a").close()
            messagebox.showinfo("Success", f"Project '{IDE.project_name}' created successfully!")
            IDE.open_project()
        create_project = ctk.CTkButton(IDE.project, text="Create Project", font=('Arial', 15),command=create_project_callback)
        create_project.grid(row=4, column=0, pady=(10, 10))
        IDE.project.mainloop()
        
    @staticmethod
    def open_project():
        if getattr(IDE, 'project', None):
            try:
                IDE.project.destroy()
            except Exception:
                pass
        if not IDE.project_location:
            messagebox.showwarning("Error", "No Project is currently loaded")
            return
        if not os.path.exists(IDE.project_location):
            messagebox.showwarning("Error", "The Project Location Doesn't Exist Anymore\nIt might have been deleted")
            IDE.project_name = None
            IDE.project_location = None
            IDE.version = None
            IDE.project_description = None
            with open(project_appdata_project_file, "w") as f:
                f.write("")
            return
        IDE.project = ctk.CTk() 
        IDE.project.attributes('-topmost', True)
        try:
            IDE.project.wm_iconbitmap("icon/lide.ico")
        except Exception:
            pass
        def open_file():
            global current_file, is_saved, extension
            IDE.project.attributes('-topmost', False)
            path = filedialog.askopenfilename(initialdir=IDE.project_location,title="Select a file",filetypes=(("All files", "*.*"),))
            if not path:
                return
            current_file = path
            extension = Path(current_file).suffix
            IDE.editor.delete("1.0", "end")
            IDE.editor.insert("1.0", "Loading large file, please wait...\n")
            IDE.editor.update_idletasks()
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
                        IDE.editor.delete("1.0", "end")
                        IDE.editor.insert("1.0", content)
                        highlight_syntax()
                        IDE.update_line_count()
                        update_title()
                        with open(file_name, "w", encoding="utf-8") as f:
                            f.write(current_file)
                        is_saved = True
                    root.after(0, insert_content)
                except Exception as e:
                    root.after(0, lambda: messagebox.showerror("Error", f"Failed to load file:\n{e}"))
            threading.Thread(target=load_large_file, daemon=True).start()
            if not IDE.project:
                pass
            else:
                IDE.project.destroy()
                
        def new():
            global current_file, is_saved
            IDE.project.attributes('-topmost', False)
            name = simpledialog.askstring("Input", "Enter file name with extension:")
            if not name:
                return
            folder = filedialog.askdirectory(initialdir=IDE.project_location,title="Select folder to save file")
            if not folder:
                return
            current_file = os.path.join(folder, name)
            open(current_file, "w").close()
            content = IDE.editor.get("1.0", "end-1c")
            IDE.editor.delete("1.0", "end")
            IDE.editor.insert("1.0", content)
            highlight_syntax()
            is_saved = True
            with open(file_name, "w") as f:
               f.write(current_file)
            update_title()
            if not IDE.project:
                pass
            else:
                IDE.project.destroy()
            IDE.update_preview_content()    
            
        def delete():
            with open(project_appdata_project_file, "w") as f:
                f.write("")
            IDE.project.attributes('-topmost', False)
            answer = messagebox.askyesno("Confirm delete" ,"Are You sure you want to delete this project")
            if answer:
                delete_path = os.path.join(IDE.project_location, "Project_Config.ini")
                if os.path.exists(delete_path):
                    os.remove(delete_path)
                    IDE.project_name = None
                    IDE.project_location = None
                    IDE.version = None
                    IDE.project_description = None
                    if getattr(IDE, 'project', None):
                        try:
                            IDE.project.destroy()
                        except Exception:
                            pass
                IDE.project_name = None
                IDE.project_location = None
                IDE.version = None
                IDE.project_description = None
                if getattr(IDE, 'project', None):
                    try:
                        IDE.project.destroy()
                    except Exception:
                        pass 
            else:
                IDE.project.attributes('-topmost', True)
        IDE.project.resizable(False, False)
        IDE.project.geometry("600x500")
        IDE.project.title(f"Project: {IDE.project_name}")
        if IDE.project_name is None or not IDE.project_name:
            messagebox.showwarning("Error", "No Project is currently loaded")
        else:
            IDE.project.title(f"Project: {IDE.project_name}")
            Details1 = ctk.CTkLabel(IDE.project, text=f"Project Name:- {IDE.project_name}",font=("Arial",20))
            Details1.pack(pady=15)
            Details2 = ctk.CTkLabel(IDE.project, text=f"Project Location:- {IDE.project_location}",font=("Arial",20))
            Details2.pack(pady=15)
            Details3 = ctk.CTkLabel(IDE.project, text=f"Project Version:- {IDE.version}",font=("Arial",20))
            Details3.pack(pady=15)
            Details4 = ctk.CTkLabel(IDE.project, text=f"Project Name:- {IDE.project_description}",font=("Arial",20))
            Details4.pack(pady=15)
            newButton = ctk.CTkButton(IDE.project, text ="New File in Project",font=("Arial", 15),command=new)
            newButton.pack(pady=15)
            openButton = ctk.CTkButton(IDE.project, text ="Open File Project",font=("Arial", 15),command=open_file)
            openButton.pack(pady=15)
            deleteButton = ctk.CTkButton(IDE.project, text ="Delete Project",font=("Arial", 15),command=delete)
            deleteButton.pack(pady=15)
        IDE.project.mainloop()    
        
    @staticmethod
    def run_app(filetype):
        global current_file
        if not current_file:
            messagebox.showwarning("No File", "Create or open a file first!")
            return
        ext = os.path.splitext(current_file)[1].lower()
        IDE.save_file()
        if filetype == "Python":
            import shutil
            if not shutil.which("python"):
                messagebox.showerror("Python Not Found", "Python is not installed or not added to PATH.")
                return
            env = os.environ.copy()
            env.pop("TCL_LIBRARY", None)
            env.pop("TK_LIBRARY", None)
            cmd = f'python "{current_file}" & pause & exit'
            subprocess.Popen(f'start cmd /k "{cmd}"', shell=True, env=env)
            return
        if filetype == "C":
            exe = os.path.splitext(current_file)[0] + ".exe"
            cmd = f'gcc "{current_file}" -o "{exe}" && "{exe}" & pause & exit'
            subprocess.Popen(f'start cmd /k "{cmd}"', shell=True)
            return
        if filetype == "CPP":
            exe = os.path.splitext(current_file)[0] + ".exe"
            cmd = f'g++ "{current_file}" -o "{exe}" && "{exe}" & pause & exit'
            subprocess.Popen(f'start cmd /k "{cmd}"', shell=True)
            return
        if filetype == "Java":
            name = os.path.splitext(os.path.basename(current_file))[0]
            path = os.path.dirname(current_file) or '.'
            cmd = f'cd /d "{path}" && javac "{current_file}" && java {name} & pause & exit'
            subprocess.Popen(f'start cmd /k "{cmd}"', shell=True)
            return
        if filetype == "html":
            webbrowser.open(current_file)
        if filetype == "CMD":
            path = os.path.dirname(current_file) or '.'
            subprocess.Popen("start cmd", shell=True, cwd=path)      
            
    @staticmethod
    def Dark_Mode():
        global color, fg_color, bg_color, Colorbutton, line_num, line_num_fg
        if color == "white":
            color = "gray10"
            fg_color = "white"
            bg_color = "gray15"
            Colorbutton = "Dark Mode"
            line_num = "gray5"
            line_num_fg = "white"
            ctk.set_appearance_mode("dark")
        else:
            color = "white"
            fg_color = "gray10"
            bg_color = "SystemButtonFace"
            Colorbutton = "Default Mode"
            line_num = "Ghost White"
            line_num_fg = "black"
            ctk.set_appearance_mode("light")

        os.makedirs(os.path.dirname(settings_path), exist_ok=True)
        with open(settings_path, "w") as f:
            f.write(Colorbutton)
    
        if IDE.editor:
            IDE.editor.configure(fg_color=color, text_color=fg_color)
        root.configure(fg_color=bg_color)
        if IDE.preview_editor:
            IDE.preview_editor.configure(fg_color=color, text_color=fg_color)
        if IDE.line_numbers:
            IDE.line_numbers.configure(fg_color=line_num, text_color=line_num_fg)
        if IDE.line_count_label:
            IDE.line_count_label.configure(text_color=fg_color)
        if IDE.character_label:
            IDE.character_label.configure(text_color=fg_color)
        if IDE.scrollbar:
            IDE.scrollbar.configure(fg_color=line_num)

    @staticmethod
    def Color_Mode(mode):
        global color, fg_color, bg_color, Colorbutton, line_num, line_num_fg
        if mode.lower() == "default mode":
            color = "white"
            fg_color = "gray10"
            bg_color = "SystemButtonFace"
            Colorbutton = "Default Mode"
            line_num = "Ghost White"
            line_num_fg = "black"
            ctk.set_appearance_mode("light")
        else:
            color = "gray10"
            fg_color = "white"
            bg_color = "gray15"
            Colorbutton = "Dark Mode"
            line_num = "gray5"
            line_num_fg = "white"
            ctk.set_appearance_mode("dark")

        if IDE.editor:
            IDE.editor.configure(fg_color=color, text_color=fg_color)
        root.configure(fg_color=bg_color)
        if IDE.preview_editor:
            IDE.preview_editor.configure(fg_color=color, text_color=fg_color)
        if IDE.line_count_label:
            IDE.line_count_label.configure(text_color=fg_color)
        if IDE.character_label:
            IDE.character_label.configure(text_color=fg_color)
        if IDE.line_numbers:
            IDE.line_numbers.configure(fg_color=line_num, text_color=line_num_fg)
        if IDE.scrollbar:
            IDE.scrollbar.configure(fg_color=line_num)
    
    @staticmethod    
    def decompile_app():
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
        if IDE.decompile_editor is not None:
            try:
                IDE.decompile_editor.destroy()
            except:
                pass
            IDE.decompile_editor = None      
        IDE.decompile_editor = tk.Tk()
        IDE.decompile_editor.configure(bg="gray15")
        IDE.decompile_editor.attributes('-topmost', True)
        try:
            IDE.decompile_editor.wm_iconbitmap("icon/lide.ico")
        except Exception:
            pass
        IDE.decompile_editor.resizable(False, False)
        IDE.decompile_editor.geometry("600x500")
        IDE.decompile_editor.title(data)
        text_decompile = tk.Text(
            IDE.decompile_editor,
            font=("Consolas", 12),
            bg="gray15",
            fg ="white",
            wrap="none"
        )
        text_decompile.insert("0.0", formatted)
        text_decompile.pack(fill="both", expand=True)
        IDE.decompile_editor.mainloop()
        
def update_title():
    global current_file, is_saved
    name = current_file if current_file else "Untitled"
    if not is_saved:
        name = "*" + name
    root.title(f"{name} - LIDE(Lightweight Internal Development Editor)")

def on_text_change(event=None):
    global is_saved
    try:
        if IDE.editor.edit_modified():
            is_saved = False
            update_title()
            IDE.editor.edit_modified(False)
    except Exception:
        is_saved = False
        update_title()

def on_close():
    global is_saved, current_file, file_name, settings_path, Colorbutton
    result = messagebox.askyesnocancel("Confirm Exit","Do you want to save before exiting?\nUnsaved changes will be lost.")
    if result is True:
        if settings_path and Colorbutton:
            os.makedirs(os.path.dirname(settings_path), exist_ok=True)
            with open(settings_path, "w", encoding="utf-8") as f:
                f.write(Colorbutton)
        if current_file:
            with open(current_file, "w", encoding="utf-8") as f:
                f.write(IDE.editor.get("1.0", "end-1c"))
            is_saved = True
            if file_name:
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(current_file)
        if getattr(IDE, 'project', None):
            try:
                IDE.project.destroy()
            except Exception:
                pass
        root.destroy()
    elif result is False:
        root.destroy()

def auto_indent(event=None):
    ext = os.path.splitext(current_file or "")[1].lower()
    keywords = BLOCK_KEYWORDS.get(ext, BLOCK_KEYWORDS[".py"])
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

def highlight_syntax(event=None):
    ext = os.path.splitext(current_file or "")[1].lower()
    rules = HIGHLIGHT_RULES.get(ext, HIGHLIGHT_RULES[".py"])
    colors = rules["colors"]
    editor = IDE.editor
    text = editor.get("1.0", "end-1c")
    editor.tag_delete(*list(colors.keys()))
    for tag, color in colors.items():
        editor.tag_config(tag, foreground=color)
    def apply(pattern, tag, flags=0):
        for match in re.finditer(pattern, text, flags):
            editor.tag_add(tag, f"1.0+{match.start()}c", f"1.0+{match.end()}c")
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

def combined_key_release(event=None):
    IDE.on_key_release(event)
    highlight_syntax(event)

def About_section():
    messagebox.showinfo(
        "About",
        """LIDE is a Simple Text Editor

In this new version, you will get:
1) Modern UI
2) Better Responsiveness
3) Syntax Highlighting
4) Improved File Handling
5) Bug Fixes with More Tabs
6) Auto Indent"""
    )
    return

def Shortcuts_section():
    messagebox.showinfo(
        "Shortcuts",
        """Shortcuts are listed below
1) SAVE FILE - CTRL + S
2) NEW FILE - CTRL + N
3) OPEN FILE - CTRL + O
4) RUN - Python(F5) ,C (F6) ,C++ (F7) ,Java (F8) ,HTML (F9), CMD(F10)"""
    )
    return
def on_editor_mousewheel(event):
    global zoom

    ctrl_pressed = (event.state & 0x4) != 0 

    if ctrl_pressed:
        if hasattr(event, 'delta'):
            zoom += 1 if event.delta > 0 else -1
        else:
            if event.num == 4:
                zoom += 1
            elif event.num == 5:
                zoom -= 1

        zoom = max(5, min(zoom, 70))
        with open(zoom_in_appdata, "w") as f:
            f.write(str(zoom))

        IDE.editor.configure(font=("Consolas", zoom))
        if IDE.line_numbers:
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

root.bind("<Control-s>", lambda e: IDE.save_file())
root.bind("<Control-n>", lambda e: IDE.new_file())
root.bind("<Control-o>", lambda e: IDE.open_file())
root.bind("<F5>", lambda e: IDE.run_app("Python"))
root.bind("<F6>", lambda e: IDE.run_app("C"))
root.bind("<F7>", lambda e: IDE.run_app("CPP"))
root.bind("<F8>", lambda e: IDE.run_app("Java"))
root.bind("<F9>", lambda e: IDE.run_app("html"))
IDE.main()
IDE.preview()
IDE.editor.bind("<<Modified>>", on_text_change)
IDE.editor.bind("<KeyRelease>", combined_key_release)
IDE.editor.bind("<KeyRelease>", IDE.on_key_release)
IDE.editor.bind("<Button-1>", lambda e: IDE.update_line_numbers())
IDE.editor.bind("<Return>", lambda e: IDE.update_line_numbers())
IDE.editor.bind("<BackSpace>", lambda e: IDE.update_line_numbers())
IDE.editor.bind("<Configure>", lambda e: IDE.update_line_numbers())
IDE.editor.bind("<Return>", auto_indent)
IDE.editor.bind("<Control-z>", lambda e: IDE.editor.event_generate("<<Undo>>"))
IDE.editor.bind("<Control-y>", lambda e: IDE.editor.event_generate("<<Redo>>"))
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()