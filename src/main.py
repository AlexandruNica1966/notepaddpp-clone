#!/usr/bin/env python3
"""
Notepad++ Clone - Tkinter Edition
A feature-rich text editor inspired by Notepad++
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
import os
import re
import json
from pathlib import Path


class LineNumbers(tk.Canvas):
    """Line numbers margin widget"""
    
    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, width=50, highlightthickness=0, **kwargs)
        self.text_widget = text_widget
        self.text_widget.bind('<KeyRelease>', self._on_change)
        self.text_widget.bind('<MouseWheel>', self._on_change)
        self.text_widget.bind('<Button-1>', self._on_change)
        self.text_widget.bind('<Configure>', self._on_change)
        self.current_theme = {'bg': '#2b2b2b', 'fg': '#808080'}
        
    def set_theme(self, bg, fg):
        self.current_theme = {'bg': bg, 'fg': fg}
        self.config(bg=bg)
        self._on_change()
        
    def _on_change(self, event=None):
        self.redraw()
        
    def redraw(self, *args):
        self.delete('all')
        i = self.text_widget.index('@0,0')
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split('.')[0]
            self.create_text(40, y, anchor='ne', text=linenum,
                           fill=self.current_theme['fg'], font=('Consolas', 10))
            i = self.text_widget.index(f'{i}+1line')


class SyntaxHighlighter:
    """Regex-based syntax highlighting for multiple languages"""
    
    THEMES = {
        'dark': {
            'bg': '#2b2b2b', 'fg': '#d4d4d4', 'select_bg': '#264f78',
            'keyword': '#569cd6', 'string': '#ce9178', 'comment': '#6a9955',
            'number': '#b5cea8', 'function': '#dcdcaa', 'class': '#4ec9b0',
            'operator': '#d4d4d4', 'brace': '#ffd700', 'current_line': '#2d2d30'
        },
        'light': {
            'bg': '#ffffff', 'fg': '#000000', 'select_bg': '#add6ff',
            'keyword': '#0000ff', 'string': '#a31515', 'comment': '#008000',
            'number': '#098658', 'function': '#795e26', 'class': '#267f99',
            'operator': '#000000', 'brace': '#0000ff', 'current_line': '#f0f0f0'
        }
    }
    
    PATTERNS = {
        'python': {
            'keyword': r'\b(and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield|True|False|None)\b',
            'string': r'("[^"\\]*(\\.[^"\\]*)*"|\'[^\'\\]*(\\.[^\'\\]*)*\')',
            'comment': r'#.*$',
            'number': r'\b\d+\.?\d*\b',
            'function': r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
            'class': r'\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        },
        'javascript': {
            'keyword': r'\b(var|let|const|function|return|if|else|for|while|do|break|continue|switch|case|default|try|catch|finally|throw|new|delete|typeof|instanceof|in|of|class|extends|super|this|null|undefined|true|false|async|await|import|export|from)\b',
            'string': r'("[^"\\]*(\\.[^"\\]*)*"|\'[^\'\\]*(\\.[^\'\\]*)*\'|`[^`\\]*(\\.[^`\\]*)*`)',
            'comment': r'(//.*$|/\*[\s\S]*?\*/)',
            'number': r'\b\d+\.?\d*\b',
            'function': r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
        },
        'html': {
            'keyword': r'\b(html|head|body|div|span|p|a|img|ul|ol|li|table|tr|td|th|form|input|button|script|style|link|meta|title|h[1-6]|br|hr)\b',
            'string': r'("[^"]*"|\'[^\']*\')',
            'comment': r'<!--[\s\S]*?-->',
            'tag': r'</?[a-zA-Z][^>]*>',
        },
        'css': {
            'keyword': r'\b(color|background|margin|padding|border|width|height|display|position|top|left|right|bottom|font|text|float|clear|flex|grid|block|inline|none|absolute|relative|fixed|sticky)\b',
            'string': r'("[^"]*"|\'[^\']*\')',
            'comment': r'/\*[\s\S]*?\*/',
            'number': r'\b\d+\.?\d*(px|em|rem|%|vh|vw)?\b',
            'selector': r'[.#]?[a-zA-Z][a-zA-Z0-9_-]*\s*\{',
        },
        'cpp': {
            'keyword': r'\b(int|float|double|char|bool|void|if|else|for|while|do|switch|case|default|break|continue|return|class|struct|public|private|protected|virtual|static|const|new|delete|this|nullptr|true|false|namespace|using|template|typename|try|catch|throw)\b',
            'string': r'("[^"\\]*(\\.[^"\\]*)*")',
            'comment': r'(//.*$|/\*[\s\S]*?\*/)',
            'number': r'\b\d+\.?\d*\b',
            'function': r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
        },
        'java': {
            'keyword': r'\b(public|private|protected|static|final|class|interface|extends|implements|void|int|long|double|float|char|boolean|byte|short|if|else|for|while|do|switch|case|default|break|continue|return|new|this|super|null|true|false|try|catch|finally|throw|throws|import|package)\b',
            'string': r'("[^"\\]*(\\.[^"\\]*)*")',
            'comment': r'(//.*$|/\*[\s\S]*?\*/)',
            'number': r'\b\d+\.?\d*\b',
            'function': r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
        },
    }
    
    def __init__(self, text_widget, theme='dark'):
        self.text = text_widget
        self.theme = theme
        self.language = 'python'
        self._setup_tags()
        
    def _setup_tags(self):
        t = self.THEMES[self.theme]
        self.text.tag_configure('keyword', foreground=t['keyword'])
        self.text.tag_configure('string', foreground=t['string'])
        self.text.tag_configure('comment', foreground=t['comment'])
        self.text.tag_configure('number', foreground=t['number'])
        self.text.tag_configure('function', foreground=t['function'])
        self.text.tag_configure('class', foreground=t['class'])
        self.text.tag_configure('operator', foreground=t['operator'])
        self.text.tag_configure('brace', foreground=t['brace'])
        self.text.tag_configure('current_line', background=t['current_line'])
        
    def set_theme(self, theme):
        self.theme = theme
        self._setup_tags()
        
    def set_language(self, language):
        self.language = language
        
    def highlight(self, event=None):
        if self.language not in self.PATTERNS:
            return
            
        # Remove all tags
        for tag in ['keyword', 'string', 'comment', 'number', 'function', 'class']:
            self.text.tag_remove(tag, '1.0', tk.END)
            
        content = self.text.get('1.0', tk.END)
        patterns = self.PATTERNS[self.language]
        
        for tag, pattern in patterns.items():
            for match in re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE):
                start = f'1.0+{match.start()}c'
                end = f'1.0+{match.end()}c'
                self.text.tag_add(tag, start, end)
                
        # Highlight current line
        self.text.tag_remove('current_line', '1.0', tk.END)
        current_line = self.text.index(tk.INSERT).split('.')[0]
        self.text.tag_add('current_line', f'{current_line}.0', f'{current_line}.end+1c')


class EditorTab(ttk.Frame):
    """Single editor tab with text widget and line numbers"""
    
    def __init__(self, master, filepath=None, theme='dark', **kwargs):
        super().__init__(master, **kwargs)
        self.filepath = filepath
        self.encoding = 'utf-8'
        self.modified = False
        
        t = SyntaxHighlighter.THEMES[theme]
        
        # Main container
        self.paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # Editor frame
        self.editor_frame = ttk.Frame(self.paned)
        self.paned.add(self.editor_frame, weight=1)
        
        # Text widget with scrollbars
        self.text = tk.Text(
            self.editor_frame,
            wrap=tk.NONE,
            undo=True,
            maxundo=-1,
            bg=t['bg'],
            fg=t['fg'],
            insertbackground=t['fg'],
            selectbackground=t['select_bg'],
            font=('Consolas', 11),
            tabs=('1c',)
        )
        
        self.v_scroll = ttk.Scrollbar(self.editor_frame, orient=tk.VERTICAL, command=self.text.yview)
        self.h_scroll = ttk.Scrollbar(self.editor_frame, orient=tk.HORIZONTAL, command=self.text.xview)
        self.text.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        
        # Line numbers
        self.line_numbers = LineNumbers(self.editor_frame, self.text, bg=t['bg'])
        
        # Grid layout
        self.line_numbers.grid(row=0, column=0, sticky='ns')
        self.text.grid(row=0, column=1, sticky='nsew')
        self.v_scroll.grid(row=0, column=2, sticky='ns')
        self.h_scroll.grid(row=1, column=1, sticky='ew')
        
        self.editor_frame.grid_rowconfigure(0, weight=1)
        self.editor_frame.grid_columnconfigure(1, weight=1)
        
        # Syntax highlighter
        self.highlighter = SyntaxHighlighter(self.text, theme)
        
        # Bindings
        self.text.bind('<KeyRelease>', self._on_text_change)
        self.text.bind('<Button-1>', self._on_click)
        
        # Load file if provided
        if filepath:
            self.load_file(filepath)
            
    def _on_text_change(self, event=None):
        self.modified = True
        self.highlighter.highlight()
        self.line_numbers.redraw()
        self.event_generate('<<TextModified>>')
        
    def _on_click(self, event=None):
        self.line_numbers.redraw()
        self.highlighter.highlight()
        
    def load_file(self, filepath):
        """Load file content with encoding detection"""
        self.filepath = filepath
        try:
            # Try UTF-8 first
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                self.encoding = 'utf-8'
        except UnicodeDecodeError:
            # Fallback to Latin-1
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()
                self.encoding = 'latin-1'
                
        self.text.delete('1.0', tk.END)
        self.text.insert('1.0', content)
        self.modified = False
        self.highlighter.highlight()
        
        # Auto-detect language
        ext = Path(filepath).suffix.lower()
        lang_map = {'.py': 'python', '.js': 'javascript', '.html': 'html',
                   '.css': 'css', '.cpp': 'cpp', '.c': 'cpp', '.h': 'cpp', '.java': 'java'}
        if ext in lang_map:
            self.highlighter.set_language(lang_map[ext])
            
    def save_file(self, filepath=None):
        """Save content to file"""
        save_path = filepath or self.filepath
        if not save_path:
            return False
            
        content = self.text.get('1.0', tk.END + '-1c')
        with open(save_path, 'w', encoding=self.encoding) as f:
            f.write(content)
            
        self.filepath = save_path
        self.modified = False
        return True
        
    def get_title(self):
        """Get tab title"""
        if self.filepath:
            name = os.path.basename(self.filepath)
        else:
            name = 'Untitled'
        return f'{"*" if self.modified else ""}{name}'
        
    def set_theme(self, theme):
        """Apply theme colors"""
        t = SyntaxHighlighter.THEMES[theme]
        self.text.configure(bg=t['bg'], fg=t['fg'], insertbackground=t['fg'],
                          selectbackground=t['select_bg'])
        self.line_numbers.set_theme(t['bg'], t['fg'])
        self.highlighter.set_theme(theme)
        self.highlighter.highlight()


class FindReplaceDialog(tk.Toplevel):
    """Find and Replace dialog with regex support"""
    
    def __init__(self, master, text_widget):
        super().__init__(master)
        self.text = text_widget
        self.title('Find and Replace')
        self.geometry('500x200')
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        
        # Find frame
        find_frame = ttk.LabelFrame(self, text='Find')
        find_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(find_frame, text='Find what:').grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.find_entry = ttk.Entry(find_frame, width=40)
        self.find_entry.grid(row=0, column=1, padx=5, pady=2)
        self.find_entry.bind('<Return>', lambda e: self.find_next())
        
        # Replace frame
        replace_frame = ttk.LabelFrame(self, text='Replace')
        replace_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(replace_frame, text='Replace with:').grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.replace_entry = ttk.Entry(replace_frame, width=40)
        self.replace_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # Options frame
        options_frame = ttk.Frame(self)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.match_case = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text='Match case', variable=self.match_case).pack(side=tk.LEFT, padx=5)
        
        self.whole_word = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text='Whole word', variable=self.whole_word).pack(side=tk.LEFT, padx=5)
        
        self.use_regex = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text='Regex', variable=self.use_regex).pack(side=tk.LEFT, padx=5)
        
        # Buttons frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text='Find Next', command=self.find_next).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text='Replace', command=self.replace).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text='Replace All', command=self.replace_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text='Close', command=self.destroy).pack(side=tk.RIGHT, padx=2)
        
        self.find_entry.focus_set()
        
    def _build_pattern(self):
        """Build search pattern based on options"""
        pattern = self.find_entry.get()
        if not pattern:
            return None
            
        if not self.use_regex.get():
            pattern = re.escape(pattern)
            
        if self.whole_word.get():
            pattern = r'\b' + pattern + r'\b'
            
        flags = 0 if self.match_case.get() else re.IGNORECASE
        return re.compile(pattern, flags)
        
    def find_next(self):
        """Find next occurrence"""
        pattern = self._build_pattern()
        if not pattern:
            return
            
        # Get current position
        current_pos = self.text.index(tk.INSERT)
        content = self.text.get(current_pos, tk.END)
        
        # Search from current position
        match = pattern.search(content)
        if not match:
            # Wrap around to beginning
            content = self.text.get('1.0', tk.END)
            match = pattern.search(content)
            if not match:
                messagebox.showinfo('Find', 'No more occurrences found.')
                return
            start = f'1.0+{match.start()}c'
            end = f'1.0+{match.end()}c'
        else:
            start = f'{current_pos}+{match.start()}c'
            end = f'{current_pos}+{match.end()}c'
            
        # Highlight found text
        self.text.tag_remove('found', '1.0', tk.END)
        self.text.tag_add('found', start, end)
        self.text.tag_configure('found', background='yellow', foreground='black')
        self.text.mark_set(tk.INSERT, end)
        self.text.see(start)
        
    def replace(self):
        """Replace current selection"""
        try:
            sel_start = self.text.index(tk.SEL_FIRST)
            sel_end = self.text.index(tk.SEL_LAST)
            replacement = self.replace_entry.get()
            self.text.delete(sel_start, sel_end)
            self.text.insert(sel_start, replacement)
        except tk.TclError:
            self.find_next()
            
    def replace_all(self):
        """Replace all occurrences"""
        pattern = self._build_pattern()
        if not pattern:
            return
            
        content = self.text.get('1.0', tk.END)
        replacement = self.replace_entry.get()
        
        count = 0
        new_content = content
        offset = 0
        
        for match in pattern.finditer(content):
            start = f'1.0+{match.start()}c'
            end = f'1.0+{match.end()}c'
            self.text.delete(start, end)
            self.text.insert(start, replacement)
            count += 1
            offset += len(replacement) - (match.end() - match.start())
            
        if count > 0:
            messagebox.showinfo('Replace All', f'Replaced {count} occurrences.')
        else:
            messagebox.showinfo('Replace All', 'No occurrences found.')


class GotoLineDialog(tk.Toplevel):
    """Go to line dialog"""
    
    def __init__(self, master, text_widget):
        super().__init__(master)
        self.text = text_widget
        self.title('Go to Line')
        self.geometry('300x100')
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        
        ttk.Label(self, text='Line number:').pack(pady=5)
        self.entry = ttk.Entry(self, width=20)
        self.entry.pack(pady=5)
        self.entry.bind('<Return>', lambda e: self.goto())
        self.entry.focus_set()
        
        ttk.Button(self, text='Go', command=self.goto).pack(pady=5)
        
    def goto(self):
        try:
            line = int(self.entry.get())
            self.text.mark_set(tk.INSERT, f'{line}.0')
            self.text.see(f'{line}.0')
            self.text.tag_remove('current_line', '1.0', tk.END)
            self.text.tag_add('current_line', f'{line}.0', f'{line}.end+1c')
            self.destroy()
        except ValueError:
            messagebox.showerror('Error', 'Invalid line number')


class NotepadPlusPlusClone:
    """Main application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Notepad++ Clone')
        self.root.geometry('1200x800')
        
        # Settings
        self.settings_file = Path.home() / '.notepaddpp_clone.json'
        self.settings = self._load_settings()
        self.current_theme = self.settings.get('theme', 'dark')
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self._setup_styles()
        
        # Menu bar
        self._create_menu()
        
        # Toolbar
        self._create_toolbar()
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind('<Button-2>', self._close_tab_on_middle_click)
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)
        
        # Status bar
        self._create_statusbar()
        
        # Bindings
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-S>', lambda e: self.save_as())
        self.root.bind('<Control-f>', lambda e: self.show_find_dialog())
        self.root.bind('<Control-g>', lambda e: self.show_goto_dialog())
        self.root.bind('<Control-w>', lambda e: self.close_tab())
        self.root.bind('<Control-q>', lambda e: self.quit_app())
        self.root.protocol('WM_DELETE_WINDOW', self.quit_app)
        
        # New tab button
        self._create_new_tab_button()
        
        # Open initial file if exists
        if self.settings.get('last_files'):
            for f in self.settings['last_files']:
                if os.path.exists(f):
                    self.open_file(f)
        else:
            self.new_file()
            
    def _setup_styles(self):
        """Setup ttk styles"""
        t = SyntaxHighlighter.THEMES[self.current_theme]
        self.style.configure('TNotebook', background=t['bg'])
        self.style.configure('TNotebook.Tab', padding=[10, 5])
        
    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='File', menu=file_menu)
        file_menu.add_command(label='New', accelerator='Ctrl+N', command=self.new_file)
        file_menu.add_command(label='Open...', accelerator='Ctrl+O', command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label='Save', accelerator='Ctrl+S', command=self.save_file)
        file_menu.add_command(label='Save As...', accelerator='Ctrl+Shift+S', command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label='Close Tab', accelerator='Ctrl+W', command=self.close_tab)
        file_menu.add_command(label='Exit', accelerator='Ctrl+Q', command=self.quit_app)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Edit', menu=edit_menu)
        edit_menu.add_command(label='Undo', accelerator='Ctrl+Z', command=lambda: self._text_event('<<Undo>>'))
        edit_menu.add_command(label='Redo', accelerator='Ctrl+Y', command=lambda: self._text_event('<<Redo>>'))
        edit_menu.add_separator()
        edit_menu.add_command(label='Cut', accelerator='Ctrl+X', command=lambda: self._text_event('<<Cut>>'))
        edit_menu.add_command(label='Copy', accelerator='Ctrl+C', command=lambda: self._text_event('<<Copy>>'))
        edit_menu.add_command(label='Paste', accelerator='Ctrl+V', command=lambda: self._text_event('<<Paste>>'))
        edit_menu.add_separator()
        edit_menu.add_command(label='Find...', accelerator='Ctrl+F', command=self.show_find_dialog)
        edit_menu.add_command(label='Go to Line...', accelerator='Ctrl+G', command=self.show_goto_dialog)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='View', menu=view_menu)
        view_menu.add_command(label='Toggle Theme', command=self.toggle_theme)
        
        # Language menu
        lang_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Language', menu=lang_menu)
        for lang in ['python', 'javascript', 'html', 'css', 'cpp', 'java']:
            lang_menu.add_command(label=lang.capitalize(), 
                                command=lambda l=lang: self.set_language(l))
        
    def _create_toolbar(self):
        """Create toolbar"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=2, pady=2)
        
        ttk.Button(toolbar, text='New', command=self.new_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text='Open', command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text='Save', command=self.save_file).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        ttk.Button(toolbar, text='Find', command=self.show_find_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text='Theme', command=self.toggle_theme).pack(side=tk.LEFT, padx=2)
        
    def _create_statusbar(self):
        """Create status bar"""
        self.statusbar = ttk.Frame(self.root)
        self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_line = ttk.Label(self.statusbar, text='Ln 1, Col 1')
        self.status_line.pack(side=tk.LEFT, padx=5)
        
        self.status_encoding = ttk.Label(self.statusbar, text='UTF-8')
        self.status_encoding.pack(side=tk.RIGHT, padx=5)
        
        self.status_lang = ttk.Label(self.statusbar, text='Python')
        self.status_lang.pack(side=tk.RIGHT, padx=5)
        
    def _create_new_tab_button(self):
        """Create + button for new tab"""
        # This is a workaround since ttk.Notebook doesn't support custom tab widgets easily
        pass
        
    def _text_event(self, event):
        """Generate event on current text widget"""
        tab = self._get_current_tab()
        if tab:
            tab.text.event_generate(event)
            
    def _get_current_tab(self):
        """Get current EditorTab instance"""
        try:
            current = self.notebook.select()
            if current:
                return self.root.nametowidget(current)
        except tk.TclError:
            pass
        return None
        
    def _on_tab_changed(self, event=None):
        """Update statusbar when tab changes"""
        tab = self._get_current_tab()
        if tab:
            self._update_statusbar(tab)
            
    def _update_statusbar(self, tab):
        """Update status bar info"""
        cursor = tab.text.index(tk.INSERT)
        line, col = map(int, cursor.split('.'))
        self.status_line.config(text=f'Ln {line}, Col {col + 1}')
        self.status_encoding.config(text=tab.encoding.upper())
        self.status_lang.config(text=tab.highlighter.language.capitalize())
        
    def new_file(self):
        """Create new empty tab"""
        tab = EditorTab(self.notebook, theme=self.current_theme)
        self.notebook.add(tab, text=tab.get_title())
        self.notebook.select(tab)
        tab.text.focus_set()
        tab.bind('<<TextModified>>', lambda e: self._update_tab_title(tab))
        return tab
        
    def open_file(self, filepath=None):
        """Open file in new tab"""
        if not filepath:
            filepath = filedialog.askopenfilename(
                filetypes=[('All Files', '*.*'), ('Python', '*.py'),
                          ('JavaScript', '*.js'), ('HTML', '*.html'),
                          ('CSS', '*.css'), ('C++', '*.cpp *.c *.h'),
                          ('Java', '*.java'), ('Text', '*.txt')]
            )
            if not filepath:
                return
                
        # Check if already open
        for tab_id in self.notebook.tabs():
            tab = self.root.nametowidget(tab_id)
            if tab.filepath == filepath:
                self.notebook.select(tab_id)
                return
                
        tab = EditorTab(self.notebook, filepath=filepath, theme=self.current_theme)
        self.notebook.add(tab, text=tab.get_title())
        self.notebook.select(tab)
        tab.text.focus_set()
        tab.bind('<<TextModified>>', lambda e: self._update_tab_title(tab))
        self._update_statusbar(tab)
        
    def save_file(self):
        """Save current file"""
        tab = self._get_current_tab()
        if not tab:
            return
            
        if not tab.filepath:
            self.save_as()
        else:
            tab.save_file()
            self._update_tab_title(tab)
            
    def save_as(self):
        """Save current file with new name"""
        tab = self._get_current_tab()
        if not tab:
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=[('All Files', '*.*'), ('Python', '*.py'),
                      ('JavaScript', '*.js'), ('HTML', '*.html'),
                      ('CSS', '*.css'), ('Text', '*.txt')]
        )
        if filepath:
            tab.save_file(filepath)
            self._update_tab_title(tab)
            
    def close_tab(self, tab_id=None):
        """Close tab"""
        if not tab_id:
            tab_id = self.notebook.select()
            
        if not tab_id:
            return
            
        tab = self.root.nametowidget(tab_id)
        
        if tab.modified:
            response = messagebox.askyesnocancel(
                'Unsaved Changes',
                f'Save changes to {tab.get_title()}?'
            )
            if response is None:  # Cancel
                return
            elif response:  # Yes
                self.save_file()
                
        self.notebook.forget(tab_id)
        
        # Create new tab if all closed
        if not self.notebook.tabs():
            self.new_file()
            
    def _close_tab_on_middle_click(self, event):
        """Close tab on middle click"""
        try:
            tab_id = self.notebook.select()
            if tab_id:
                self.close_tab(tab_id)
        except tk.TclError:
            pass
            
    def _update_tab_title(self, tab):
        """Update tab title with modified indicator"""
        tab_id = self.notebook.select()
        if tab_id:
            self.notebook.tab(tab_id, text=tab.get_title())
            self._update_statusbar(tab)
            
    def show_find_dialog(self):
        """Show find/replace dialog"""
        tab = self._get_current_tab()
        if tab:
            FindReplaceDialog(self.root, tab.text)
            
    def show_goto_dialog(self):
        """Show goto line dialog"""
        tab = self._get_current_tab()
        if tab:
            GotoLineDialog(self.root, tab.text)
            
    def set_language(self, language):
        """Set syntax highlighting language"""
        tab = self._get_current_tab()
        if tab:
            tab.highlighter.set_language(language)
            tab.highlighter.highlight()
            self._update_statusbar(tab)
            
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self._setup_styles()
        for tab_id in self.notebook.tabs():
            tab = self.root.nametowidget(tab_id)
            tab.set_theme(self.current_theme)
            
    def _load_settings(self):
        """Load settings from file"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {'theme': 'dark', 'last_files': []}
        
    def _save_settings(self):
        """Save settings to file"""
        files = []
        for tab_id in self.notebook.tabs():
            tab = self.root.nametowidget(tab_id)
            if tab.filepath:
                files.append(tab.filepath)
                
        self.settings['theme'] = self.current_theme
        self.settings['last_files'] = files
        
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f)
            
    def quit_app(self):
        """Save settings and quit"""
        self._save_settings()
        self.root.quit()
        
    def run(self):
        """Start application"""
        self.root.mainloop()


if __name__ == '__main__':
    app = NotepadPlusPlusClone()
    app.run()
