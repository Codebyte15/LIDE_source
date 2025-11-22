"""Autosave Plugin for LIDE IDE
This plugin automatically saves the current file every 10 seconds.
"""

_autosave_running = False

def _autosave_loop(IDE):
    global _autosave_running
    if not _autosave_running:
        return
    IDE.save_file()
    IDE.root.after(10000, _autosave_loop, IDE)

def setup_plugin(IDE):
    global _autosave_running
    _autosave_running = True
    print("Autosave plugin started!")
    IDE.root.after(100, _autosave_loop, IDE)
