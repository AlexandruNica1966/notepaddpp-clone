#!/usr/bin/env python3
"""
QScintilla editor widget with syntax highlighting, code folding,
brace matching, auto-completion, bookmarks, and right-click context menu.
"""

import os
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QKeySequence, QIcon
from PyQt5.QtWidgets import QApplication, QAction, QMenu, QMessageBox
from PyQt5.Qsci import (
    QsciScintilla, QsciLexerPython, QsciLexerCPP, QsciLexerJavaScript,
    QsciLexerHTML, QsciLexerCSS, QsciLexerJSON, QsciLexerXML,
    QsciLexerSQL, QsciLexerBash, QsciLexerYAML, QsciLexerMarkdown,
    QsciLexerJava, QsciLexerMakefile, QsciLexerDiff, QsciAPIs
)

from themes import LEXER_THEMES, APP_THEMES

# Bookmark marker number
MARKER_BOOKMARK = 1
MARKER_BOOKMARK_CHAR = 0x25CF  # ● filled circle


def create_lexer_for_extension(filepath):
    """Create appropriate lexer based on file extension."""
    ext = Path(filepath).suffix.lower() if filepath else ''
    name = Path(filepath).name.lower() if filepath else ''

    lexer_map = {
        '.py': QsciLexerPython, '.pyw': QsciLexerPython,
        '.js': QsciLexerJavaScript, '.mjs': QsciLexerJavaScript,
        '.ts': QsciLexerJavaScript, '.jsx': QsciLexerJavaScript,
        '.html': QsciLexerHTML, '.htm': QsciLexerHTML, '.php': QsciLexerHTML,
        '.css': QsciLexerCSS, '.scss': QsciLexerCSS,
        '.json': QsciLexerJSON,
        '.xml': QsciLexerXML, '.svg': QsciLexerXML, '.xaml': QsciLexerXML,
        '.sql': QsciLexerSQL,
        '.sh': QsciLexerBash, '.bash': QsciLexerBash, '.zsh': QsciLexerBash,
        '.yaml': QsciLexerYAML, '.yml': QsciLexerYAML,
        '.md': QsciLexerMarkdown, '.markdown': QsciLexerMarkdown,
        '.java': QsciLexerJava,
        '.cpp': QsciLexerCPP, '.c': QsciLexerCPP, '.h': QsciLexerCPP,
        '.hpp': QsciLexerCPP, '.cc': QsciLexerCPP, '.cs': QsciLexerCPP,
        '.diff': QsciLexerDiff, '.patch': QsciLexerDiff,
    }

    if name == 'Makefile':
        return QsciLexerMakefile()

    lexer_class = lexer_map.get(ext)
    if lexer_class:
        return lexer_class()
    return None


def get_language_name(lexer):
    """Return human-readable language name from lexer."""
    lexer_names = {
        QsciLexerPython: 'Python', QsciLexerCPP: 'C++',
        QsciLexerJavaScript: 'JavaScript', QsciLexerHTML: 'HTML',
        QsciLexerCSS: 'CSS', QsciLexerJSON: 'JSON', QsciLexerXML: 'XML',
        QsciLexerSQL: 'SQL', QsciLexerBash: 'Bash', QsciLexerYAML: 'YAML',
        QsciLexerMarkdown: 'Markdown', QsciLexerJava: 'Java',
        QsciLexerMakefile: 'Makefile', QsciLexerDiff: 'Diff',
    }
    return lexer_names.get(type(lexer), 'Text')


class EditorWidget(QsciScintilla):
    """QScintilla-based editor widget with full Notepad++ features."""

    modificationChanged = pyqtSignal(bool)
    cursorPositionChanged = pyqtSignal(int, int)
    closeTabRequested = pyqtSignal()
    languageChanged = pyqtSignal(str)

    def __init__(self, parent=None, filepath=None, theme='dark'):
        super().__init__(parent)
        self.filepath = filepath
        self._encoding = 'utf-8'
        self._theme = theme
        self._lexer = None
        self._api = None

        self._setup_editor()
        self._setup_margins()
        self._setup_bookmarks()

        if filepath:
            self._load_file(filepath)
            self._lexer = create_lexer_for_extension(filepath)
        else:
            self._lexer = QsciLexerPython()

        if self._lexer:
            self._apply_lexer(self._lexer)

        self._apply_theme(theme)

        # Signals
        self.modificationChanged.connect(self._on_modified)

    def _setup_editor(self):
        """Configure base editor settings."""
        import sys
        if sys.platform == 'win32':
            font = QFont('Consolas', 14)
        else:
            font = QFont('DejaVu Sans Mono', 14)
        font.setBold(True)
        font.setWeight(QFont.DemiBold)
        self.setFont(font)
        self.setUtf8(True)
        self.setEolMode(QsciScintilla.EolUnix)

        # Indentation
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setAutoIndent(True)
        self.setBackspaceUnindents(True)
        self.setIndentationGuides(True)
        self.setIndentationWidth(0)  # Same as tab width

        # Visual
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        self.setCaretLineVisible(True)
        self.setCaretWidth(2)
        self.setSelectionBackgroundColor(QColor('#264f78'))

        # Wrap
        self.setWrapMode(QsciScintilla.WrapNone)
        self.setWrapVisualFlags(QsciScintilla.WrapFlagNone)

        # Visibility
        self.setWhitespaceVisibility(QsciScintilla.WsInvisible)
        self.setEolVisibility(False)

        # Edge
        self.setEdgeMode(QsciScintilla.EdgeNone)

        # Auto-completion
        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setAutoCompletionThreshold(3)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionReplaceWord(True)

        # Scrolling
        self.SendScintilla(QsciScintilla.SCI_SETSCROLLWIDTHTRACKING, 1)

    def _setup_margins(self):
        """Configure margins for line numbers, bookmarks, folding."""
        # Margin 0: Line numbers
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, '0000')
        self.setMarginsForegroundColor(QColor('#858585'))

        # Margin 1: Bookmark symbols
        self.setMarginType(1, QsciScintilla.SymbolMargin)
        self.setMarginWidth(1, 16)
        self.setMarginSensitivity(1, True)
        self.marginClicked.connect(self._on_margin_clicked)

        # Margin 2: Code folding
        self.setMarginType(2, QsciScintilla.SymbolMargin)
        self.setMarginWidth(2, 16)

        # Enable folding
        self.setFolding(QsciScintilla.BoxedTreeFoldStyle)
        self.setFoldMarginColors(
            QColor('#3c3c3c'), QColor('#3c3c3c')
        )

    def _setup_bookmarks(self):
        """Configure bookmark markers."""
        self.markerDefine(
            QsciScintilla.Circle, MARKER_BOOKMARK
        )
        self.setMarkerBackgroundColor(
            QColor('#007acc'), MARKER_BOOKMARK
        )

    def _on_margin_clicked(self, margin, line, modifier):
        """Handle margin clicks for bookmark toggle."""
        if margin == 1:  # Bookmark margin
            self._toggle_bookmark(line)

    def _toggle_bookmark(self, line):
        """Toggle bookmark on a line."""
        if self.markersAtLine(line) & (1 << MARKER_BOOKMARK):
            self.markerDelete(line, MARKER_BOOKMARK)
        else:
            self.markerAdd(line, MARKER_BOOKMARK)

    def next_bookmark(self):
        """Go to next bookmark."""
        line, _ = self.getCursorPosition()
        next_line = self.markerFindNext(line + 1, 1 << MARKER_BOOKMARK)
        if next_line >= 0:
            self.setCursorPosition(next_line, 0)
            self.ensureLineVisible(next_line)
        else:
            # Wrap around
            next_line = self.markerFindNext(0, 1 << MARKER_BOOKMARK)
            if next_line >= 0:
                self.setCursorPosition(next_line, 0)
                self.ensureLineVisible(next_line)

    def prev_bookmark(self):
        """Go to previous bookmark."""
        line, _ = self.getCursorPosition()
        prev_line = self.markerFindPrevious(line - 1, 1 << MARKER_BOOKMARK)
        if prev_line >= 0:
            self.setCursorPosition(prev_line, 0)
            self.ensureLineVisible(prev_line)
        else:
            # Wrap around
            lines = self.lines()
            prev_line = self.markerFindPrevious(lines, 1 << MARKER_BOOKMARK)
            if prev_line >= 0:
                self.setCursorPosition(prev_line, 0)
                self.ensureLineVisible(prev_line)

    def _apply_lexer(self, lexer):
        """Install and configure a QsciLexer."""
        self._lexer = lexer
        lexer.setDefaultFont(self.font())
        self.setLexer(lexer)

        # API auto-completion for Python
        if isinstance(lexer, QsciLexerPython):
            self._api = QsciAPIs(lexer)
            keywords = [
                'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
                'del', 'elif', 'else', 'except', 'finally', 'for', 'from',
                'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal',
                'not', 'or', 'pass', 'raise', 'return', 'try', 'while',
                'with', 'yield', 'True', 'False', 'None', 'async', 'await',
                'print', 'len', 'range', 'enumerate', 'zip', 'map', 'filter',
                'int', 'str', 'float', 'list', 'dict', 'set', 'tuple', 'bool',
                'open', 'super', 'self', 'type', 'isinstance', 'hasattr',
                'getattr', 'setattr', 'import', '__init__', '__name__',
                '__main__', 'append', 'extend', 'pop', 'keys', 'values',
                'items', 'split', 'join', 'strip', 'replace', 'format',
                'sorted', 'reversed', 'max', 'min', 'sum', 'any', 'all',
            ]
            for kw in keywords:
                self._api.add(kw)
            self._api.prepare()
        else:
            self._api = None

        self.languageChanged.emit(get_language_name(lexer))

    def _apply_theme(self, theme_name):
        """Apply color theme to editor and lexer."""
        self._theme = theme_name
        theme = APP_THEMES.get(theme_name, APP_THEMES['dark'])

        # Scintilla colors via SendScintilla
        style_default = 32
        self.SendScintilla(QsciScintilla.SCI_STYLESETFORE, style_default, theme['font'].rgb() & 0xFFFFFF)
        self.SendScintilla(QsciScintilla.SCI_STYLESETBACK, style_default, theme['paper'].rgb() & 0xFFFFFF)
        self.SendScintilla(QsciScintilla.SCI_STYLESETSIZE, style_default, 11)
        self.SendScintilla(QsciScintilla.SCI_STYLECLEARALL, 0, 0)

        # Caret
        self.setCaretForegroundColor(theme['caret'])

        # Margins
        self.setMarginsBackgroundColor(theme['margin_bg'])
        self.setMarginsForegroundColor(theme['margin_fg'])
        self.setFoldMarginColors(theme['fold_bg'], theme['fold_bg'])
        self.setCaretLineBackgroundColor(theme['caret_line'])

        # Selection
        self.setSelectionBackgroundColor(theme['selection'])
        self.setSelectionForegroundColor(theme.get('selection_fg', theme['font']))

        # Edge line
        self.setEdgeColor(theme.get('edge', theme['margin_bg']))

        # Matched brace
        self.setMatchedBraceBackgroundColor(theme.get('brace_match_bg', QColor('#3a3a3a')))
        self.setMatchedBraceForegroundColor(theme.get('brace_match_fg', theme['font']))

        # Unmatched brace
        self.setUnmatchedBraceForegroundColor(theme.get('brace_bad', QColor('#ff0000')))

        self.setPaper(theme['paper'])

        # Apply lexer theme
        if self._lexer:
            lexer_name = type(self._lexer).__name__
            lexer_themes = LEXER_THEMES.get(theme_name, {})
            lexer_theme = lexer_themes.get(lexer_name, {})

            self._lexer.setDefaultPaper(theme['paper'])
            self._lexer.setDefaultColor(theme['font'])
            self._lexer.setDefaultFont(self.font())

            # Apply per-style colors
            for style_num, style_def in lexer_theme.items():
                if isinstance(style_def, dict):
                    if 'fg' in style_def:
                        self._lexer.setColor(style_def['fg'], style_num)
                    if 'bg' in style_def:
                        self._lexer.setPaper(style_def['bg'], style_num)
                    if 'font_style' in style_def:
                        font = QFont(self.font())
                        if style_def['font_style'] == 'bold':
                            font.setBold(True)
                        elif style_def['font_style'] == 'italic':
                            font.setItalic(True)
                        elif style_def['font_style'] == 'bold_italic':
                            font.setBold(True)
                            font.setItalic(True)
                        self._lexer.setFont(font, style_num)

    def set_theme(self, theme_name):
        """Public method to change theme."""
        self._apply_theme(theme_name)

    def _load_file(self, filepath):
        """Load file with encoding detection."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                self._encoding = 'utf-8'
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()
                self._encoding = 'latin-1'

        self.setText(content)
        self.setModified(False)
        self.filepath = filepath

    def save_file(self, filepath=None):
        """Save content to file."""
        save_path = filepath or self.filepath
        if not save_path:
            return False
        with open(save_path, 'w', encoding=self._encoding) as f:
            f.write(self.text())
        self.setModified(False)
        self.filepath = save_path
        return True

    def _on_modified(self, modified):
        """Emit signal when modification state changes."""
        self.modificationChanged.emit(modified)

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, value):
        self._encoding = value

    @property
    def language(self):
        return get_language_name(self._lexer) if self._lexer else 'Text'

    def get_tab_title(self):
        """Get display title for the tab."""
        if self.filepath:
            name = os.path.basename(self.filepath)
        else:
            name = 'new ' + str(id(self))[-4:]
        prefix = '*' if self.isModified() else ''
        return f'{prefix}{name}'

    def get_eol_text(self):
        """Get EOL mode as text."""
        mode = self.eolMode()
        return {QsciScintilla.EolWindows: 'CRLF',
                QsciScintilla.EolUnix: 'LF',
                QsciScintilla.EolMac: 'CR'}.get(mode, 'LF')

    # ─── Copy/Paste/Cut overrides for context menu ───

    def copy(self):
        super().copy()

    def cut(self):
        super().cut()

    def paste(self):
        super().paste()

    # ─── Line operations ───

    def duplicate_line(self):
        """Duplicate current line."""
        line, _ = self.getCursorPosition()
        text = self.text(line)
        self.insertAt(text + ('\n' if line < self.lines() - 1 else '\n' + text),
                      line, 0)
        self.setCursorPosition(line + 1, 0)

    def delete_line(self):
        """Delete current line."""
        line, _ = self.getCursorPosition()
        self.setSelection(line, 0, line + 1, 0)
        self.removeSelectedText()

    def move_line_up(self):
        """Move current line up."""
        line, _ = self.getCursorPosition()
        if line <= 0:
            return
        text = self.text(line)
        self.setSelection(line, 0, line + 1, 0)
        self.removeSelectedText()
        self.insertAt(text + '\n', line - 1, 0)
        self.setCursorPosition(line - 1, 0)

    def move_line_down(self):
        """Move current line down."""
        line, _ = self.getCursorPosition()
        if line >= self.lines() - 1:
            return
        text = self.text(line)
        self.setSelection(line, 0, line + 1, 0)
        self.removeSelectedText()
        self.insertAt(text + '\n', line + 1, 0)
        if line + 1 < self.lines() - 1:
            self.insertAt('\n', line + 1, 0)
            self.setSelection(line + 1, 0, line + 2, 0)
            self.removeSelectedText()
        self.setCursorPosition(line + 1, 0)

    def join_lines(self):
        """Join current line with next."""
        line, _ = self.getCursorPosition()
        if line >= self.lines() - 1:
            return
        end_pos = self.lineLength(line)
        next_start = self.positionFromLineIndex(line + 1, 0)
        self.setSelection(line, end_pos, line + 1, 0)
        self.removeSelectedText()
        # Remove leading whitespace from joined line
        next_text = self.text(line).lstrip()
        if next_text:
            # place cursor at join position
            total = self.positionFromLineIndex(line, 0) + self.lineLength(line)
            line_len = self.lineLength(line)
            self.setCursorPosition(line, line_len)

    # ─── Comment toggling ───

    def toggle_line_comment(self):
        """Toggle line comment (like Notepad++ Ctrl+Q)."""
        if self.hasSelectedText():
            # Get selected lines
            start_line, _, end_line, _ = self.getSelection()
            for line in range(start_line, end_line + 1):
                self._toggle_single_line_comment(line)
            self.setSelection(start_line, 0, end_line + 1, 0)
        else:
            line, _ = self.getCursorPosition()
            self._toggle_single_line_comment(line)

    def _toggle_single_line_comment(self, line):
        """Toggle comment on a single line."""
        comment_char = '// ' if isinstance(self._lexer, (QsciLexerCPP,
            QsciLexerJavaScript, QsciLexerJava)) else '# '
        text = self.text(line).lstrip()
        if text.startswith(comment_char.strip()):
            # Remove comment
            leading = self.text(line)[:len(self.text(line)) - len(self.text(line).lstrip())]
            uncommented = text[len(comment_char.strip()):]
            if uncommented.startswith(' '):
                uncommented = uncommented[1:]
            self.setSelection(line, 0, line + 1, 0)
            self.removeSelectedText()
            self.insertAt(leading + uncommented + '\n', line, 0)
        else:
            # Add comment
            leading = self.text(line)[:len(self.text(line)) - len(text)]
            self.setSelection(line, 0, line + 1, 0)
            self.removeSelectedText()
            self.insertAt(leading + comment_char + text + '\n', line, 0)

    # ─── Case conversion ───

    def to_uppercase(self):
        """Convert selection to uppercase."""
        if self.hasSelectedText():
            start, _, end, _ = self.getSelection()
            text = self.selectedText()
            self.removeSelectedText()
            self.insertAt(text.upper(), start, 0)
            self.setSelection(start, 0, end, 0)

    def to_lowercase(self):
        """Convert selection to lowercase."""
        if self.hasSelectedText():
            start, _, end, _ = self.getSelection()
            text = self.selectedText()
            self.removeSelectedText()
            self.insertAt(text.lower(), start, 0)
            self.setSelection(start, 0, end, 0)

    # ─── Misc ───

    def trim_trailing_whitespace(self):
        """Remove trailing whitespace from all lines."""
        lines = self.lines()
        for line in range(lines):
            text = self.text(line)
            stripped = text.rstrip()
            if stripped != text:
                self.setSelection(line, len(stripped), line, len(text))
                self.removeSelectedText()

    def open_containing_folder(self):
        """Open file manager at file location."""
        if self.filepath and os.path.exists(self.filepath):
            folder = os.path.dirname(os.path.abspath(self.filepath))
            import subprocess, sys
            if sys.platform == 'win32':
                subprocess.Popen(['explorer', folder], shell=True)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', folder])
            else:
                subprocess.Popen(['xdg-open', folder])

    def convert_eols(self, mode):
        """Convert line endings."""
        self.convertEols(mode)
        # Also set the mode for future saves
        self.setEolMode(mode)

    # ─── CONTEXT MENU (RIGHT-CLICK) ───

    def contextMenuEvent(self, event):
        """Show right-click context menu."""
        menu = QMenu(self)

        # Edit actions
        cut_action = QAction('Cut', self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.cut)
        menu.addAction(cut_action)

        copy_action = QAction('Copy', self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy)
        menu.addAction(copy_action)

        paste_action = QAction('Paste', self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste)
        menu.addAction(paste_action)

        delete_action = QAction('Delete', self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self.removeSelectedText)
        menu.addAction(delete_action)

        menu.addSeparator()

        select_all = QAction('Select All', self)
        select_all.setShortcut(QKeySequence.SelectAll)
        select_all.triggered.connect(self.selectAll)
        menu.addAction(select_all)

        menu.addSeparator()

        undo_action = QAction('Undo', self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.undo)
        menu.addAction(undo_action)

        redo_action = QAction('Redo', self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.redo)
        menu.addAction(redo_action)

        menu.addSeparator()

        # Comment toggling
        comment_action = QAction('Toggle Line Comment', self)
        comment_action.setShortcut('Ctrl+Q')
        comment_action.triggered.connect(self.toggle_line_comment)
        menu.addAction(comment_action)

        menu.addSeparator()

        # Line operations
        duplicate_action = QAction('Duplicate Line', self)
        duplicate_action.setShortcut('Ctrl+D')
        duplicate_action.triggered.connect(self.duplicate_line)
        menu.addAction(duplicate_action)

        delete_line_action = QAction('Delete Line', self)
        delete_line_action.setShortcut('Ctrl+L')
        delete_line_action.triggered.connect(self.delete_line)
        menu.addAction(delete_line_action)

        menu.addSeparator()

        # Case conversion
        upper_action = QAction('UPPERCASE', self)
        upper_action.setShortcut('Ctrl+Shift+U')
        upper_action.triggered.connect(self.to_uppercase)
        menu.addAction(upper_action)

        lower_action = QAction('lowercase', self)
        lower_action.setShortcut('Ctrl+U')
        lower_action.triggered.connect(self.to_lowercase)
        menu.addAction(lower_action)

        menu.addSeparator()

        # Bookmarks
        line, _ = self.getCursorPosition()
        has_bookmark = bool(self.markersAtLine(line) & (1 << MARKER_BOOKMARK))
        if has_bookmark:
            bm_action = QAction('Remove Bookmark', self)
        else:
            bm_action = QAction('Toggle Bookmark', self)
        bm_action.setShortcut('Ctrl+F2')
        bm_action.triggered.connect(lambda: self._toggle_bookmark(line))
        menu.addAction(bm_action)

        menu.addSeparator()

        # File operations
        open_folder_action = QAction('Open Containing Folder', self)
        open_folder_action.triggered.connect(self.open_containing_folder)
        menu.addAction(open_folder_action)

        close_tab_action = QAction('Close Tab', self)
        close_tab_action.setShortcut('Ctrl+W')
        close_tab_action.triggered.connect(self.closeTabRequested.emit)
        menu.addAction(close_tab_action)

        menu.exec_(event.globalPos())
