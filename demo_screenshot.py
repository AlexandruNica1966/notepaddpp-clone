#!/usr/bin/env python3
"""Create a demo screenshot of the Notepad++ Clone"""

import tkinter as tk
import sys
import os

os.environ['DISPLAY'] = ':99'
sys.path.insert(0, 'src')

from main import NotepadPlusPlusClone

app = NotepadPlusPlusClone()
app.new_file()
tab = app._get_current_tab()

sample_code = '''# Notepad++ Clone - Tkinter Edition
# Features:
# - Multiple tabs with close buttons
# - Line numbers margin
# - Syntax highlighting (Python, JS, HTML, CSS, C++, Java)
# - Find/Replace with regex support
# - Dark/Light themes
# - Session persistence
# - Encoding detection

def hello_world():
    """Sample Python code with syntax highlighting"""
    print("Hello, World!")
    return 42

class MyClass:
    def __init__(self):
        self.value = 100
        
    def method(self):
        return self.value * 2
        
# Comments are highlighted
# Strings too: "like this" and 'this'
# Numbers: 123, 45.67
'''

tab.text.insert('1.0', sample_code)
tab.highlighter.highlight()
tab.line_numbers.redraw()
app.root.update()

# Save screenshot using Tkinter's postscript (requires ghostscript)
# Or just save the window state
app.root.after(2000, app.root.quit)
app.root.mainloop()

print("Demo completed - check if window displayed correctly")
