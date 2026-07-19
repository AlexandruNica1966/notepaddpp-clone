#!/usr/bin/env python3
"""
Notepad++ Clone - Qt Edition
A full-featured text editor using PyQt5 + QScintilla.

Run: python3 main.py
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QStyleFactory
from mainwindow import MainWindow

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName('Notepad++ Clone')
    app.setOrganizationName('Hermes')

    # Force Fusion style for consistent dark theme (title bar too)
    app.setStyle('Fusion')

    # Dark palette for window chrome (title bar, borders)
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor('#1e1e1e'))
    dark_palette.setColor(QPalette.WindowText, QColor('#d4d4d4'))
    dark_palette.setColor(QPalette.Base, QColor('#252526'))
    dark_palette.setColor(QPalette.AlternateBase, QColor('#2d2d30'))
    dark_palette.setColor(QPalette.ToolTipBase, QColor('#2d2d30'))
    dark_palette.setColor(QPalette.ToolTipText, QColor('#d4d4d4'))
    dark_palette.setColor(QPalette.Text, QColor('#d4d4d4'))
    dark_palette.setColor(QPalette.Button, QColor('#3c3c3c'))
    dark_palette.setColor(QPalette.ButtonText, QColor('#d4d4d4'))
    dark_palette.setColor(QPalette.BrightText, QColor('#ff0000'))
    dark_palette.setColor(QPalette.Link, QColor('#007acc'))
    dark_palette.setColor(QPalette.Highlight, QColor('#264f78'))
    dark_palette.setColor(QPalette.HighlightedText, QColor('#ffffff'))
    dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor('#666666'))
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor('#666666'))
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor('#666666'))
    app.setPalette(dark_palette)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
