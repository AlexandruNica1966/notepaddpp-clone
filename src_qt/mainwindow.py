#!/usr/bin/env python3
"""
MainWindow for Notepad++ Qt Clone.
Features: multi-tab editing, split view, menu bar, toolbar, status bar,
keyboard shortcuts, drag&drop, session persistence, recent files.
"""

import os
import json
from pathlib import Path

from PyQt5.QtCore import Qt, QSize, QSettings, pyqtSignal
from PyQt5.QtGui import QKeySequence, QFont, QIcon
from PyQt5.QtWidgets import (
    QMainWindow, QAction, QMenu, QMenuBar, QToolBar,
    QStatusBar, QTabWidget, QTabBar, QSplitter, QMessageBox,
    QFileDialog, QApplication, QLabel, QWidget, QVBoxLayout,
    QStyle,
)
from PyQt5.Qsci import QsciScintilla

from editor import EditorWidget, create_lexer_for_extension, get_language_name
from findreplace import FindReplaceDialog, GotoLineDialog
from themes import APP_THEMES, get_app_stylesheet


class EditorTabWidget(QTabWidget):
    """Tab widget for editor tabs with close button support."""

    tabCloseRequested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.tabCloseRequested.connect(self._close_tab)

    def add_editor_tab(self, editor, index=None):
        """Add an editor tab."""
        title = editor.get_tab_title()
        if index is not None:
            idx = self.insertTab(index, editor, title)
        else:
            idx = self.addTab(editor, title)
        self.setCurrentWidget(editor)
        editor.modificationChanged.connect(
            lambda m, e=editor: self._update_tab_title(e)
        )
        return idx

    def _update_tab_title(self, editor):
        """Refresh tab title when modification state changes."""
        for i in range(self.count()):
            if self.widget(i) == editor:
                self.setTabText(i, editor.get_tab_title())
                break

    def _close_tab(self, index):
        """Handle tab close request."""
        editor = self.widget(index)
        if editor and editor.isModified():
            ret = QMessageBox.question(
                self, 'Unsaved Changes',
                f'Save changes to {editor.get_tab_title()}?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if ret == QMessageBox.Cancel:
                return
            if ret == QMessageBox.Yes:
                self.parent().parent().save_file()
        self.removeTab(index)


class MainWindow(QMainWindow):
    """Notepad++ Clone main window."""

    def __init__(self):
        super().__init__()
        self._settings_file = Path.home() / '.notepaddpp_qt.json'
        self._settings = self._load_settings()
        self._theme = self._settings.get('theme', 'dark')
        self._split_mode = 'none'
        self._find_dialog = None
        self._goto_dialog = None

        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_shortcuts()
        self._apply_theme()
        self._restore_session()

    def _setup_ui(self):
        """Initialize the UI layout."""
        self.setWindowTitle('Notepad++ Clone - Qt Edition')
        self.resize(1200, 800)
        self.setAcceptDrops(True)

        # Central widget: QSplitter for split view
        self._splitter = QSplitter(Qt.Horizontal, self)
        self._left_tabs = EditorTabWidget(self._splitter)
        self._right_tabs = None  # Created on demand for split view
        self._splitter.addWidget(self._left_tabs)
        self.setCentralWidget(self._splitter)

        # Status bar
        self._statusbar = self.statusBar()
        self._cursor_label = QLabel('Ln 1, Col 1')
        self._cursor_label.setMinimumWidth(150)
        self._statusbar.addPermanentWidget(self._cursor_label)

        self._sel_label = QLabel('Sel: 0')
        self._statusbar.addPermanentWidget(self._sel_label)

        self._lang_label = QLabel('Python')
        self._statusbar.addPermanentWidget(self._lang_label)

        self._eol_label = QLabel('LF')
        self._statusbar.addPermanentWidget(self._eol_label)

        self._encoding_label = QLabel('UTF-8')
        self._statusbar.addPermanentWidget(self._encoding_label)

        self._statusbar.setStyleSheet(
            f"QStatusBar {{ background-color: {APP_THEMES[self._theme]['statusbar_bg']}; "
            f"color: {APP_THEMES[self._theme]['statusbar_fg']}; }}"
        )

        # Track tab changes
        self._left_tabs.currentChanged.connect(self._on_tab_changed)

    def _setup_menu(self):
        """Create menu bar."""
        menubar = self.menuBar()

        # Larger menu font
        menu_font = menubar.font()
        menu_font.setPointSize(12)
        menubar.setFont(menu_font)

        # ── File menu ──
        file_menu = menubar.addMenu('&File')

        self._add_action(file_menu, '&New', 'Ctrl+N', 'New file', self.new_file)
        self._add_action(file_menu, '&Open...', 'Ctrl+O', 'Open file', self.open_file)
        file_menu.addSeparator()
        self._add_action(file_menu, '&Save', 'Ctrl+S', 'Save file', self.save_file)
        self._add_action(file_menu, 'Save &As...', 'Ctrl+Shift+S', 'Save as', self.save_as)
        self._add_action(file_menu, 'Save A&ll', 'Ctrl+Alt+S', 'Save all', self.save_all)
        file_menu.addSeparator()
        self._add_action(file_menu, '&Close Tab', 'Ctrl+W', 'Close tab', self.close_tab)
        self._add_action(file_menu, 'Close &All', 'Ctrl+Shift+W', 'Close all', self.close_all)
        file_menu.addSeparator()
        self._add_action(file_menu, 'E&xit', 'Ctrl+Q', 'Exit', self.close)

        # ── Edit menu ──
        edit_menu = menubar.addMenu('&Edit')
        self._add_action(edit_menu, '&Undo', 'Ctrl+Z', 'Undo', self._editor_send, 'Undo')
        self._add_action(edit_menu, '&Redo', 'Ctrl+Y', 'Redo', self._editor_send, 'Redo')
        edit_menu.addSeparator()
        self._add_action(edit_menu, 'Cu&t', 'Ctrl+X', 'Cut', self._editor_send, 'Cut')
        self._add_action(edit_menu, '&Copy', 'Ctrl+C', 'Copy', self._editor_send, 'Copy')
        self._add_action(edit_menu, '&Paste', 'Ctrl+V', 'Paste', self._editor_send, 'Paste')
        self._add_action(edit_menu, '&Delete', 'Del', 'Delete', lambda: self._current_editor() and self._current_editor().removeSelectedText())
        edit_menu.addSeparator()
        self._add_action(edit_menu, 'Select &All', 'Ctrl+A', 'Select all', self._editor_send, 'SelectAll')
        edit_menu.addSeparator()
        self._add_action(edit_menu, '&Find...', 'Ctrl+F', 'Find', self.show_find)
        self._add_action(edit_menu, '&Replace...', 'Ctrl+H', 'Replace', self.show_find)
        self._add_action(edit_menu, 'Go to &Line...', 'Ctrl+G', 'Go to line', self.show_goto)
        edit_menu.addSeparator()
        self._add_action(edit_menu, 'Toggle Line &Comment', 'Ctrl+Q', 'Toggle comment',
                        lambda: self._current_editor() and self._current_editor().toggle_line_comment())
        self._add_action(edit_menu, 'Duplicate Line', 'Ctrl+D', 'Duplicate line',
                        lambda: self._current_editor() and self._current_editor().duplicate_line())
        self._add_action(edit_menu, 'Delete Line', 'Ctrl+L', 'Delete line',
                        lambda: self._current_editor() and self._current_editor().delete_line())
        self._add_action(edit_menu, 'Join Lines', 'Ctrl+J', 'Join lines',
                        lambda: self._current_editor() and self._current_editor().join_lines())
        edit_menu.addSeparator()
        self._add_action(edit_menu, '&UPPERCASE', 'Ctrl+Shift+U', 'To uppercase',
                        lambda: self._current_editor() and self._current_editor().to_uppercase())
        self._add_action(edit_menu, '&lowercase', 'Ctrl+U', 'To lowercase',
                        lambda: self._current_editor() and self._current_editor().to_lowercase())
        edit_menu.addSeparator()
        self._add_action(edit_menu, 'Trim Trailing Space', '', 'Trim trailing whitespace',
                        lambda: self._current_editor() and self._current_editor().trim_trailing_whitespace())

        # ── Search menu ──
        search_menu = menubar.addMenu('&Search')
        self._add_action(search_menu, '&Find...', 'Ctrl+F', 'Find text', self.show_find)
        self._add_action(search_menu, '&Replace...', 'Ctrl+H', 'Replace text', self.show_find)
        self._add_action(search_menu, 'Find &Next', 'F3', 'Next match', self.find_next_shortcut)
        self._add_action(search_menu, 'Find &Previous', 'Shift+F3', 'Previous match', self.find_prev_shortcut)
        search_menu.addSeparator()
        self._add_action(search_menu, 'Go to &Line...', 'Ctrl+G', 'Go to line', self.show_goto)
        search_menu.addSeparator()
        self._add_action(search_menu, 'Next Bookmark', 'F2', 'Go to next bookmark',
                        lambda: self._current_editor() and self._current_editor().next_bookmark())
        self._add_action(search_menu, 'Previous Bookmark', 'Shift+F2', 'Go to prev bookmark',
                        lambda: self._current_editor() and self._current_editor().prev_bookmark())

        # ── View menu ──
        view_menu = menubar.addMenu('&View')
        self._add_action(view_menu, 'Toggle &Theme', 'F11', 'Switch dark/light', self.toggle_theme)
        view_menu.addSeparator()
        self._add_action(view_menu, 'Toggle &Word Wrap', 'Ctrl+Alt+W', 'Toggle word wrap', self.toggle_word_wrap)
        self._wrap_action = view_menu.addAction('Word Wrap')
        self._wrap_action.setCheckable(True)
        self._wrap_action.triggered.connect(self.toggle_word_wrap)
        self._add_action(view_menu, 'Show &Whitespace', 'Ctrl+Shift+W', 'Toggle whitespace',
                        self.toggle_whitespace)
        self._add_action(view_menu, 'Show &EOL', 'Ctrl+Shift+E', 'Toggle EOL',
                        self.toggle_eol_visibility)
        view_menu.addSeparator()
        self._add_action(view_menu, '&Zoom In', 'Ctrl++', 'Zoom in', self.zoom_in)
        self._add_action(view_menu, '&Zoom Out', 'Ctrl+-', 'Zoom out', self.zoom_out)
        self._add_action(view_menu, '&Reset Zoom', 'Ctrl+0', 'Reset zoom', self.zoom_reset)
        view_menu.addSeparator()

        split_menu = view_menu.addMenu('Split View')
        self._add_action(split_menu, 'None', '', 'No split', lambda: self._set_split_mode('none'))
        self._add_action(split_menu, 'Horizontal Split', '', 'Top/bottom', lambda: self._set_split_mode('horizontal'))
        self._add_action(split_menu, 'Vertical Split', '', 'Left/right', lambda: self._set_split_mode('vertical'))

        # ── Encoding menu ──
        enc_menu = menubar.addMenu('&Encoding')
        self._add_action(enc_menu, 'UTF-8', '', 'Set UTF-8', lambda: self._set_encoding('utf-8'))
        self._add_action(enc_menu, 'Latin-1 (ISO 8859-1)', '', 'Set Latin-1', lambda: self._set_encoding('latin-1'))

        # ── EOL Conversion ──
        eol_menu = menubar.addMenu('&EOL Conversion')
        self._add_action(eol_menu, 'Unix (LF)', '', 'Convert to LF',
                        lambda: self._convert_eol(QsciScintilla.EolUnix))
        self._add_action(eol_menu, 'Windows (CR LF)', '', 'Convert to CRLF',
                        lambda: self._convert_eol(QsciScintilla.EolWindows))
        self._add_action(eol_menu, 'Old Mac (CR)', '', 'Convert to CR',
                        lambda: self._convert_eol(QsciScintilla.EolMac))

        # ── Language menu ──
        lang_menu = menubar.addMenu('&Language')
        languages = [
            ('Python', '.py'), ('C++', '.cpp'), ('JavaScript', '.js'),
            ('HTML', '.html'), ('CSS', '.css'), ('JSON', '.json'),
            ('XML', '.xml'), ('SQL', '.sql'), ('Bash', '.sh'),
            ('YAML', '.yaml'), ('Markdown', '.md'), ('Java', '.java'),
            ('Makefile', 'Makefile'), ('Diff', '.diff'),
        ]
        for name, ext in languages:
            lang_sub = lang_menu.addAction(name)
            lang_sub.triggered.connect(lambda _, e=ext: self._set_language_by_ext(e))

    def _add_action(self, menu, text, shortcut, tooltip, callback, *args):
        """Helper to add menu actions."""
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        if tooltip:
            action.setToolTip(tooltip)
        if args:
            # For editor commands where callback needs args
            action.triggered.connect(lambda: callback(args[0]))
        else:
            action.triggered.connect(callback)
        menu.addAction(action)
        return action

    def _setup_toolbar(self):
        """Create toolbar."""
        toolbar = QToolBar('Main Toolbar', self)
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        new_btn = QAction(self.style().standardIcon(QStyle.SP_FileIcon), 'New', self)
        new_btn.setToolTip('New (Ctrl+N)')
        new_btn.triggered.connect(self.new_file)
        toolbar.addAction(new_btn)

        open_btn = QAction(self.style().standardIcon(QStyle.SP_DialogOpenButton), 'Open', self)
        open_btn.setToolTip('Open (Ctrl+O)')
        open_btn.triggered.connect(self.open_file)
        toolbar.addAction(open_btn)

        save_btn = QAction(self.style().standardIcon(QStyle.SP_DialogSaveButton), 'Save', self)
        save_btn.setToolTip('Save (Ctrl+S)')
        save_btn.triggered.connect(self.save_file)
        toolbar.addAction(save_btn)

        toolbar.addSeparator()

        find_btn = QAction(self.style().standardIcon(QStyle.SP_FileDialogContentsView), 'Find', self)
        find_btn.setToolTip('Find (Ctrl+F)')
        find_btn.triggered.connect(self.show_find)
        toolbar.addAction(find_btn)

        toolbar.addSeparator()

        theme_btn = QAction('🌓', self)
        theme_btn.setToolTip('Toggle Theme')
        theme_btn.triggered.connect(self.toggle_theme)
        toolbar.addAction(theme_btn)

    def _setup_shortcuts(self):
        """Additional keyboard shortcuts not in menus."""
        pass  # Most shortcuts are on menu actions

    def _current_editor(self):
        """Get the currently active editor widget."""
        widget = self._left_tabs.currentWidget()
        if isinstance(widget, QSplitter):
            return None
        return widget if isinstance(widget, EditorWidget) else None

    def _active_tab_widget(self):
        """Get the tab widget that currently has focus."""
        current = QApplication.focusWidget()
        while current:
            if isinstance(current, EditorTabWidget):
                return current
            current = current.parent()
        return self._left_tabs

    def _editor_send(self, method_name):
        """Send a method call to the current editor."""
        editor = self._current_editor()
        if editor:
            getattr(editor, method_name)()

    def new_file(self, language_ext=None):
        """Create a new empty tab."""
        editor = EditorWidget(self, theme=self._theme)
        editor.cursorPositionChanged.connect(self._update_statusbar)
        editor.languageChanged.connect(self._update_lang_status)
        editor.closeTabRequested.connect(self.close_tab)

        if language_ext:
            lexer = create_lexer_for_extension(language_ext)
            if lexer:
                editor._apply_lexer(lexer)
                editor._apply_theme(self._theme)

        tabs = self._active_tab_widget()
        tabs.add_editor_tab(editor)
        editor.setFocus()
        self._update_statusbar(*editor.getCursorPosition())

    def open_file(self, filepath=None):
        """Open a file in a new tab."""
        if not filepath:
            filepath, _ = QFileDialog.getOpenFileName(
                self, 'Open File', '',
                'All Files (*);;Python (*.py);;JavaScript (*.js);;HTML (*.html);;'
                'CSS (*.css);;JSON (*.json);;XML (*.xml);;SQL (*.sql);;'
                'C++ (*.cpp *.c *.h);;Java (*.java);;Text (*.txt)'
            )
            if not filepath:
                return

        # Check if already open
        for i in range(self._left_tabs.count()):
            e = self._left_tabs.widget(i)
            if isinstance(e, EditorWidget) and e.filepath == filepath:
                self._left_tabs.setCurrentIndex(i)
                return

        editor = EditorWidget(self, filepath=filepath, theme=self._theme)
        editor.cursorPositionChanged.connect(self._update_statusbar)
        editor.languageChanged.connect(self._update_lang_status)
        editor.closeTabRequested.connect(self.close_tab)

        self._left_tabs.add_editor_tab(editor)
        editor.setFocus()
        self._update_statusbar(*editor.getCursorPosition())

        # Add to recent files
        self._add_recent_file(filepath)

    def save_file(self):
        """Save current file."""
        editor = self._current_editor()
        if not editor:
            return
        if not editor.filepath:
            self.save_as()
        else:
            editor.save_file()

    def save_as(self):
        """Save current file under a new name."""
        editor = self._current_editor()
        if not editor:
            return
        filepath, _ = QFileDialog.getSaveFileName(
            self, 'Save As', '',
            'All Files (*);;Python (*.py);;JavaScript (*.js);;HTML (*.html);;'
            'CSS (*.css);;JSON (*.json);;Text (*.txt)'
        )
        if filepath:
            editor.save_file(filepath)
            self._update_tab_title(editor)
            self._add_recent_file(filepath)

    def save_all(self):
        """Save all open files."""
        for i in range(self._left_tabs.count()):
            e = self._left_tabs.widget(i)
            if isinstance(e, EditorWidget) and e.isModified():
                e.save_file()

    def close_tab(self, index=None):
        """Close a specific tab or the current one."""
        tabs = self._active_tab_widget()
        if index is None:
            index = tabs.currentIndex()
        if index < 0:
            return
        editor = tabs.widget(index)
        if isinstance(editor, EditorWidget) and editor.isModified():
            ret = QMessageBox.question(
                self, 'Unsaved Changes',
                f'Save changes to {editor.get_tab_title()}?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if ret == QMessageBox.Cancel:
                return
            if ret == QMessageBox.Yes:
                editor.save_file()
        tabs.removeTab(index)

    def close_all(self):
        """Close all tabs."""
        while self._left_tabs.count() > 0:
            editor = self._left_tabs.widget(0)
            if isinstance(editor, EditorWidget) and editor.isModified():
                ret = QMessageBox.question(
                    self, 'Unsaved Changes',
                    f'Save changes to {editor.get_tab_title()}?',
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                )
                if ret == QMessageBox.Cancel:
                    return
                if ret == QMessageBox.Yes:
                    editor.save_file()
            self._left_tabs.removeTab(0)

    def _update_tab_title(self, editor):
        """Update the tab title."""
        for i in range(self._left_tabs.count()):
            if self._left_tabs.widget(i) == editor:
                self._left_tabs.setTabText(i, editor.get_tab_title())
                break

    def show_find(self):
        """Show find/replace dialog."""
        editor = self._current_editor()
        if not editor:
            return
        if not self._find_dialog:
            self._find_dialog = FindReplaceDialog(self, editor)
        else:
            self._find_dialog.editor = editor
        self._find_dialog.show()
        self._find_dialog.raise_()
        self._find_dialog.find_entry.setFocus()

    def show_goto(self):
        """Show go to line dialog."""
        editor = self._current_editor()
        if not editor:
            return
        self._goto_dialog = GotoLineDialog(self, editor)
        self._goto_dialog.exec_()

    def find_next_shortcut(self):
        """Find next from shortcut (reuse last find dialog)."""
        if self._find_dialog and self._find_dialog.isVisible():
            self._find_dialog.find_next()

    def find_prev_shortcut(self):
        """Find previous from shortcut."""
        if self._find_dialog and self._find_dialog.isVisible():
            self._find_dialog.find_prev()

    def _update_statusbar(self, line, col):
        """Update status bar position info."""
        self._cursor_label.setText(f'Ln {line + 1}, Col {col + 1}')
        editor = self._current_editor()
        if editor and editor.hasSelectedText():
            sel = editor.selectedText()
            self._sel_label.setText(f'Sel: {len(sel)}')
        else:
            self._sel_label.setText('Sel: 0')
        if editor:
            self._eol_label.setText(editor.get_eol_text())
            self._encoding_label.setText(editor.encoding.upper())

    def _update_lang_status(self, lang):
        """Update language label in statusbar."""
        self._lang_label.setText(lang)

    def _on_tab_changed(self, index):
        """Handle tab switch."""
        editor = self._current_editor()
        if editor:
            line, col = editor.getCursorPosition()
            self._update_statusbar(line, col)
            self._update_lang_status(editor.language)
            editor.cursorPositionChanged.connect(self._update_statusbar)
            editor.languageChanged.connect(self._update_lang_status)

    def toggle_theme(self):
        """Toggle between dark and light theme."""
        self._theme = 'light' if self._theme == 'dark' else 'dark'
        self._apply_theme()
        self._save_settings()

    def _apply_theme(self):
        """Apply theme to all widgets."""
        self.setStyleSheet(get_app_stylesheet(self._theme))
        theme = APP_THEMES[self._theme]
        self._statusbar.setStyleSheet(
            f"QStatusBar {{ background-color: {theme['statusbar_bg']}; "
            f"color: {theme['statusbar_fg']}; }}"
        )
        for i in range(self._left_tabs.count()):
            e = self._left_tabs.widget(i)
            if isinstance(e, EditorWidget):
                e._apply_theme(self._theme)

    def toggle_word_wrap(self):
        """Toggle word wrap mode."""
        editor = self._current_editor()
        if editor:
            if editor.wrapMode() == QsciScintilla.WrapNone:
                editor.setWrapMode(QsciScintilla.WrapWord)
                self._wrap_action.setChecked(True)
            else:
                editor.setWrapMode(QsciScintilla.WrapNone)
                self._wrap_action.setChecked(False)

    def toggle_whitespace(self):
        """Toggle whitespace visibility."""
        editor = self._current_editor()
        if editor:
            if editor.wsVisible():
                editor.setWhitespaceVisibility(QsciScintilla.WsInvisible)
            else:
                editor.setWhitespaceVisibility(QsciScintilla.WsVisible)

    def toggle_eol_visibility(self):
        """Toggle EOL marker visibility."""
        editor = self._current_editor()
        if editor:
            editor.setEolVisibility(not editor.eolVisibility())

    def zoom_in(self):
        editor = self._current_editor()
        if editor:
            editor.zoomIn(1)

    def zoom_out(self):
        editor = self._current_editor()
        if editor:
            editor.zoomOut(1)

    def zoom_reset(self):
        editor = self._current_editor()
        if editor:
            editor.zoomTo(0)

    def _set_split_mode(self, mode):
        """Configure split view."""
        self._split_mode = mode
        if mode == 'none':
            if self._right_tabs:
                self._right_tabs.hide()
        elif mode == 'vertical':
            self._splitter.setOrientation(Qt.Horizontal)
            if not self._right_tabs:
                self._right_tabs = EditorTabWidget(self._splitter)
                self._splitter.addWidget(self._right_tabs)
            self._right_tabs.show()
        elif mode == 'horizontal':
            self._splitter.setOrientation(Qt.Vertical)
            if not self._right_tabs:
                self._right_tabs = EditorTabWidget(self._splitter)
                self._splitter.addWidget(self._right_tabs)
            self._right_tabs.show()

    def _set_encoding(self, encoding):
        """Set encoding for current editor."""
        editor = self._current_editor()
        if editor:
            editor.encoding = encoding
            self._encoding_label.setText(encoding.upper())

    def _convert_eol(self, mode):
        """Convert line endings."""
        editor = self._current_editor()
        if editor:
            editor.convert_eols(mode)

    def _set_language_by_ext(self, ext):
        """Set language for current editor by file extension."""
        editor = self._current_editor()
        if editor and ext:
            lexer = create_lexer_for_extension(ext)
            if lexer:
                editor._apply_lexer(lexer)
                editor._apply_theme(self._theme)

    def _add_recent_file(self, filepath):
        """Add file to recent files list."""
        recent = self._settings.get('recent_files', [])
        if filepath in recent:
            recent.remove(filepath)
        recent.insert(0, filepath)
        self._settings['recent_files'] = recent[:15]
        self._save_settings()

    # ─── Session management ───

    def _load_settings(self):
        """Load settings from JSON file."""
        if self._settings_file.exists():
            try:
                with open(self._settings_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {'theme': 'dark', 'recent_files': [], 'open_files': []}

    def _save_settings(self):
        """Save settings to JSON file."""
        files = []
        for i in range(self._left_tabs.count()):
            e = self._left_tabs.widget(i)
            if isinstance(e, EditorWidget) and e.filepath:
                files.append(e.filepath)

        self._settings['theme'] = self._theme
        self._settings['open_files'] = files

        with open(self._settings_file, 'w') as f:
            json.dump(self._settings, f)

    def _restore_session(self):
        """Reopen files from last session."""
        for filepath in self._settings.get('open_files', []):
            if os.path.exists(filepath):
                self.open_file(filepath)
        if self._left_tabs.count() == 0:
            self.new_file()

    def closeEvent(self, event):
        """Save session on close."""
        # Check unsaved changes
        for i in range(self._left_tabs.count()):
            e = self._left_tabs.widget(i)
            if isinstance(e, EditorWidget) and e.isModified():
                ret = QMessageBox.question(
                    self, 'Unsaved Changes',
                    'You have unsaved files. Save before closing?',
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                )
                if ret == QMessageBox.Cancel:
                    event.ignore()
                    return
                if ret == QMessageBox.Yes:
                    self.save_all()
                break

        self._save_settings()
        super().closeEvent(event)

    # ─── Drag & drop ───

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            if os.path.isfile(filepath):
                self.open_file(filepath)
