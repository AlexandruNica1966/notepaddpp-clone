#!/usr/bin/env python3
"""Find and Replace dialog with regex support for QScintilla editors."""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence, QColor, QTextCursor
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QCheckBox, QPushButton, QGroupBox, QGridLayout, QMessageBox,
)
from PyQt5.Qsci import QsciScintilla


class FindReplaceDialog(QDialog):
    """Non-modal find and replace dialog."""

    def __init__(self, parent=None, editor=None):
        super().__init__(parent)
        self.editor = editor
        self._last_find_pos = 0
        self._found_count = 0
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle('Find and Replace')
        self.setMinimumWidth(520)
        self.setMinimumHeight(240)

        layout = QVBoxLayout(self)

        # Find section
        find_group = QGroupBox('Find')
        find_layout = QGridLayout(find_group)

        find_layout.addWidget(QLabel('Find what:'), 0, 0)
        self.find_entry = QLineEdit()
        self.find_entry.setPlaceholderText('Enter text to find...')
        find_layout.addWidget(self.find_entry, 0, 1)

        find_layout.addWidget(QLabel('Replace with:'), 1, 0)
        self.replace_entry = QLineEdit()
        self.replace_entry.setPlaceholderText('Enter replacement text...')
        find_layout.addWidget(self.replace_entry, 1, 1)

        layout.addWidget(find_group)

        # Options section
        options_group = QGroupBox('Options')
        options_layout = QHBoxLayout(options_group)

        self.match_case = QCheckBox('Match case')
        options_layout.addWidget(self.match_case)

        self.whole_word = QCheckBox('Whole word')
        options_layout.addWidget(self.whole_word)

        self.use_regex = QCheckBox('Regex')
        options_layout.addWidget(self.use_regex)

        self.wrap_search = QCheckBox('Wrap around')
        self.wrap_search.setChecked(True)
        options_layout.addWidget(self.wrap_search)

        self.in_selection = QCheckBox('In selection')
        options_layout.addWidget(self.in_selection)

        layout.addWidget(options_group)

        # Buttons section
        btn_layout = QHBoxLayout()

        find_next_btn = QPushButton('Find Next')
        find_next_btn.clicked.connect(self.find_next)
        btn_layout.addWidget(find_next_btn)

        find_prev_btn = QPushButton('Find Previous')
        find_prev_btn.clicked.connect(self.find_prev)
        btn_layout.addWidget(find_prev_btn)

        replace_btn = QPushButton('Replace')
        replace_btn.clicked.connect(self.replace)
        btn_layout.addWidget(replace_btn)

        replace_all_btn = QPushButton('Replace All')
        replace_all_btn.clicked.connect(self.replace_all)
        btn_layout.addWidget(replace_all_btn)

        count_btn = QPushButton('Count')
        count_btn.clicked.connect(self.count_occurrences)
        btn_layout.addWidget(count_btn)

        close_btn = QPushButton('Close')
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        # Connect Enter key
        self.find_entry.returnPressed.connect(self.find_next)

    def _get_search_flags(self):
        """Build search flags from UI state."""
        flags = 0
        if self.match_case.isChecked():
            flags |= QsciScintilla.SCFIND_MATCHCASE
        if self.whole_word.isChecked():
            flags |= QsciScintilla.SCFIND_WHOLEWORD
        if self.use_regex.isChecked():
            flags |= QsciScintilla.SCFIND_REGEXP
        return flags

    def _find(self, forward=True):
        """Perform find operation."""
        if not self.editor:
            return False

        query = self.find_entry.text()
        if not query:
            return False

        flags = self._get_search_flags()

        if forward:
            if self.wrap_search.isChecked() and not self.in_selection.isChecked():
                flags |= QsciScintilla.SCFIND_WRAPAROUND

            result = self.editor.findFirst(query, False, False, False,
                                          self.in_selection.isChecked(),
                                          forward, -1, -1)
        else:
            line, col = self.editor.getCursorPosition()
            result = self.editor.findFirst(query, False, False, False,
                                          False, False, line, col)

        if not result:
            # Try from beginning if wrap is on
            if self.wrap_search.isChecked() and forward:
                self.editor.setCursorPosition(0, 0)
                result = self.editor.findFirst(query, False, False, False,
                                              False, True, -1, -1)

        return result

    def find_next(self):
        """Find next occurrence."""
        if not self._find(forward=True):
            QMessageBox.information(self, 'Find', 'No more occurrences found.')

    def find_prev(self):
        """Find previous occurrence."""
        if not self._find(forward=False):
            QMessageBox.information(self, 'Find', 'No previous occurrences found.')

    def replace(self):
        """Replace current selection."""
        if not self.editor:
            return
        if self.editor.hasSelectedText():
            selection = self.editor.selectedText()
            query = self.find_entry.text()
            if self.match_case.isChecked():
                if selection != query:
                    self.find_next()
                    return
            elif selection.lower() != query.lower():
                self.find_next()
                return
            self.editor.replaceSelectedText(self.replace_entry.text())
            self.find_next()
        else:
            self.find_next()

    def replace_all(self):
        """Replace all occurrences."""
        if not self.editor:
            return
        query = self.find_entry.text()
        if not query:
            return

        flags = self._get_search_flags()

        # Save cursor
        line, col = self.editor.getCursorPosition()

        # Go to beginning
        self.editor.setCursorPosition(0, 0)

        count = 0
        while self.editor.findFirst(query, False, False, False, False,
                                    True, -1, -1):
            self.editor.replaceSelectedText(self.replace_entry.text())
            count += 1

        if count > 0:
            QMessageBox.information(self, 'Replace All',
                                   f'Replaced {count} occurrences.')
        else:
            QMessageBox.information(self, 'Replace All',
                                   'No occurrences found.')
            self.editor.setCursorPosition(line, col)

    def count_occurrences(self):
        """Count all occurrences."""
        if not self.editor:
            return
        query = self.find_entry.text()
        if not query:
            return

        flags = self._get_search_flags()
        line, col = self.editor.getCursorPosition()

        self.editor.setCursorPosition(0, 0)
        count = 0
        while self.editor.findFirst(query, False, False, False, False,
                                    True, -1, -1):
            count += 1

        self.editor.setCursorPosition(line, col)
        QMessageBox.information(self, 'Count',
                               f'Found {count} occurrences.')


class GotoLineDialog(QDialog):
    """Go to line dialog."""

    def __init__(self, parent=None, editor=None):
        super().__init__(parent)
        self.editor = editor
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle('Go to Line')
        self.setFixedSize(300, 120)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel('Enter line number:'))

        self.line_entry = QLineEdit()
        self.line_entry.setPlaceholderText('Line number...')
        self.line_entry.returnPressed.connect(self.goto_line)
        layout.addWidget(self.line_entry)

        btn_layout = QHBoxLayout()
        go_btn = QPushButton('Go')
        go_btn.clicked.connect(self.goto_line)
        btn_layout.addWidget(go_btn)

        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def goto_line(self):
        """Navigate to the specified line."""
        if not self.editor:
            return
        try:
            line = int(self.line_entry.text()) - 1  # Convert to 0-based
            if line < 0:
                line = 0
            if line >= self.editor.lines():
                line = self.editor.lines() - 1
            self.editor.setCursorPosition(line, 0)
            self.editor.ensureLineVisible(line)
            self.accept()
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Please enter a valid line number.')
