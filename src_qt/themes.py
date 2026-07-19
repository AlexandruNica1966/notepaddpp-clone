#!/usr/bin/env python3
"""Theme definitions — dark/light with per-lexer syntax colors. All constants verified."""

from PyQt5.QtGui import QColor
from PyQt5.Qsci import (
    QsciLexerPython, QsciLexerCPP, QsciLexerJavaScript,
    QsciLexerHTML, QsciLexerCSS, QsciLexerJSON, QsciLexerXML,
    QsciLexerSQL, QsciLexerBash, QsciLexerYAML, QsciLexerMarkdown,
    QsciLexerJava, QsciLexerMakefile, QsciLexerDiff,
)

APP_THEMES = {
    'dark': {
        'paper': QColor('#1e1e1e'), 'font': QColor('#d4d4d4'),
        'caret': QColor('#d4d4d4'), 'margin_bg': QColor('#252526'),
        'margin_fg': QColor('#858585'), 'fold_bg': QColor('#3c3c3c'),
        'caret_line': QColor('#2b2b2b'), 'selection': QColor('#264f78'),
        'edge': QColor('#404040'), 'brace_match_bg': QColor('#515c6a'),
        'brace_bad': QColor('#ff0000'), 'app_bg': '#1e1e1e',
        'app_fg': '#d4d4d4', 'toolbar_bg': '#2d2d30', 'menu_bg': '#2d2d30',
        'menu_fg': '#cccccc', 'statusbar_bg': '#007acc', 'statusbar_fg': '#ffffff',
        'tab_bg': '#2d2d30', 'tab_fg': '#cccccc',
        'tab_active_bg': '#1e1e1e', 'tab_active_fg': '#ffffff',
    },
    'light': {
        'paper': QColor('#ffffff'), 'font': QColor('#000000'),
        'caret': QColor('#000000'), 'margin_bg': QColor('#f0f0f0'),
        'margin_fg': QColor('#999999'), 'fold_bg': QColor('#e8e8e8'),
        'caret_line': QColor('#f5f5f5'), 'selection': QColor('#add6ff'),
        'edge': QColor('#cccccc'), 'brace_match_bg': QColor('#c0e0ff'),
        'brace_bad': QColor('#ff0000'), 'app_bg': '#ffffff',
        'app_fg': '#000000', 'toolbar_bg': '#f0f0f0', 'menu_bg': '#f0f0f0',
        'menu_fg': '#000000', 'statusbar_bg': '#007acc', 'statusbar_fg': '#ffffff',
        'tab_bg': '#f0f0f0', 'tab_fg': '#666666',
        'tab_active_bg': '#ffffff', 'tab_active_fg': '#000000',
    },
}

LEXER_THEMES = {
    'dark': {
        'QsciLexerPython': {
            QsciLexerPython.Default: {'fg': QColor('#d4d4d4')},
            QsciLexerPython.Comment: {'fg': QColor('#6a9955'), 'font_style': 'italic'},
            QsciLexerPython.Number: {'fg': QColor('#b5cea8')},
            QsciLexerPython.Keyword: {'fg': QColor('#569cd6'), 'font_style': 'bold'},
            QsciLexerPython.DoubleQuotedString: {'fg': QColor('#ce9178')},
            QsciLexerPython.SingleQuotedString: {'fg': QColor('#ce9178')},
            QsciLexerPython.ClassName: {'fg': QColor('#4ec9b0')},
            QsciLexerPython.FunctionMethodName: {'fg': QColor('#dcdcaa')},
            QsciLexerPython.Operator: {'fg': QColor('#d4d4d4')},
            QsciLexerPython.Identifier: {'fg': QColor('#9cdcfe')},
            QsciLexerPython.CommentBlock: {'fg': QColor('#6a9955'), 'font_style': 'italic'},
            QsciLexerPython.Decorator: {'fg': QColor('#dcdcaa')},
        },
        'QsciLexerCPP': {
            QsciLexerCPP.Default: {'fg': QColor('#d4d4d4')},
            QsciLexerCPP.Comment: {'fg': QColor('#6a9955')},
            QsciLexerCPP.CommentLine: {'fg': QColor('#6a9955'), 'font_style': 'italic'},
            QsciLexerCPP.Number: {'fg': QColor('#b5cea8')},
            QsciLexerCPP.Keyword: {'fg': QColor('#569cd6'), 'font_style': 'bold'},
            QsciLexerCPP.DoubleQuotedString: {'fg': QColor('#ce9178')},
            QsciLexerCPP.SingleQuotedString: {'fg': QColor('#ce9178')},
            QsciLexerCPP.PreProcessor: {'fg': QColor('#9b9b9b')},
            QsciLexerCPP.Operator: {'fg': QColor('#d4d4d4')},
            QsciLexerCPP.Identifier: {'fg': QColor('#9cdcfe')},
        },
        'QsciLexerJavaScript': {
            QsciLexerJavaScript.Default: {'fg': QColor('#d4d4d4')},
            QsciLexerJavaScript.Comment: {'fg': QColor('#6a9955')},
            QsciLexerJavaScript.CommentLine: {'fg': QColor('#6a9955'), 'font_style': 'italic'},
            QsciLexerJavaScript.Number: {'fg': QColor('#b5cea8')},
            QsciLexerJavaScript.Keyword: {'fg': QColor('#569cd6'), 'font_style': 'bold'},
            QsciLexerJavaScript.DoubleQuotedString: {'fg': QColor('#ce9178')},
            QsciLexerJavaScript.SingleQuotedString: {'fg': QColor('#ce9178')},
        },
        'QsciLexerHTML': {
            QsciLexerHTML.Default: {'fg': QColor('#d4d4d4')},
            QsciLexerHTML.Tag: {'fg': QColor('#569cd6')},
            QsciLexerHTML.Attribute: {'fg': QColor('#9cdcfe')},
            QsciLexerHTML.HTMLNumber: {'fg': QColor('#b5cea8')},
            QsciLexerHTML.HTMLDoubleQuotedString: {'fg': QColor('#ce9178')},
            QsciLexerHTML.HTMLSingleQuotedString: {'fg': QColor('#ce9178')},
            QsciLexerHTML.HTMLComment: {'fg': QColor('#6a9955'), 'font_style': 'italic'},
            QsciLexerHTML.Entity: {'fg': QColor('#d7ba7d')},
            QsciLexerHTML.HTMLValue: {'fg': QColor('#ce9178')},
        },
        'QsciLexerCSS': {
            QsciLexerCSS.Default: {'fg': QColor('#d4d4d4')},
            QsciLexerCSS.Tag: {'fg': QColor('#569cd6')},
            QsciLexerCSS.ClassSelector: {'fg': QColor('#d7ba7d')},
            QsciLexerCSS.PseudoClass: {'fg': QColor('#d7ba7d')},
            QsciLexerCSS.CSS1Property: {'fg': QColor('#9cdcfe')},
            QsciLexerCSS.Value: {'fg': QColor('#ce9178')},
            QsciLexerCSS.Comment: {'fg': QColor('#6a9955'), 'font_style': 'italic'},
            QsciLexerCSS.IDSelector: {'fg': QColor('#d7ba7d')},
        },
        'QsciLexerJSON': {
            QsciLexerJSON.Default: {'fg': QColor('#d4d4d4')},
            QsciLexerJSON.Number: {'fg': QColor('#b5cea8')},
            QsciLexerJSON.String: {'fg': QColor('#ce9178')},
            QsciLexerJSON.Keyword: {'fg': QColor('#569cd6')},
            QsciLexerJSON.Property: {'fg': QColor('#9cdcfe')},
            QsciLexerJSON.Error: {'fg': QColor('#f44747')},
        },
        'QsciLexerSQL': {
            QsciLexerSQL.Default: {'fg': QColor('#d4d4d4')},
            QsciLexerSQL.Comment: {'fg': QColor('#6a9955')},
            QsciLexerSQL.Number: {'fg': QColor('#b5cea8')},
            QsciLexerSQL.Keyword: {'fg': QColor('#569cd6'), 'font_style': 'bold'},
            QsciLexerSQL.SingleQuotedString: {'fg': QColor('#ce9178')},
            QsciLexerSQL.DoubleQuotedString: {'fg': QColor('#ce9178')},
            QsciLexerSQL.Identifier: {'fg': QColor('#9cdcfe')},
            QsciLexerSQL.Operator: {'fg': QColor('#d4d4d4')},
        },
        'QsciLexerBash': {
            QsciLexerBash.Default: {'fg': QColor('#d4d4d4')},
            QsciLexerBash.Comment: {'fg': QColor('#6a9955'), 'font_style': 'italic'},
            QsciLexerBash.Number: {'fg': QColor('#b5cea8')},
            QsciLexerBash.Keyword: {'fg': QColor('#569cd6'), 'font_style': 'bold'},
            QsciLexerBash.DoubleQuotedString: {'fg': QColor('#ce9178')},
            QsciLexerBash.SingleQuotedString: {'fg': QColor('#ce9178')},
            QsciLexerBash.Identifier: {'fg': QColor('#9cdcfe')},
            QsciLexerBash.Scalar: {'fg': QColor('#4ec9b0')},
            QsciLexerBash.ParameterExpansion: {'fg': QColor('#dcdcaa')},
        },
        'QsciLexerJava': {
            QsciLexerJava.Default: {'fg': QColor('#d4d4d4')},
            QsciLexerJava.Comment: {'fg': QColor('#6a9955')},
            QsciLexerJava.CommentLine: {'fg': QColor('#6a9955'), 'font_style': 'italic'},
            QsciLexerJava.Number: {'fg': QColor('#b5cea8')},
            QsciLexerJava.Keyword: {'fg': QColor('#569cd6'), 'font_style': 'bold'},
            QsciLexerJava.DoubleQuotedString: {'fg': QColor('#ce9178')},
            QsciLexerJava.SingleQuotedString: {'fg': QColor('#ce9178')},
            QsciLexerJava.Identifier: {'fg': QColor('#9cdcfe')},
            QsciLexerJava.Operator: {'fg': QColor('#d4d4d4')},
        },
    },
    'light': {
        'QsciLexerPython': {
            QsciLexerPython.Default: {'fg': QColor('#000000')},
            QsciLexerPython.Comment: {'fg': QColor('#008000'), 'font_style': 'italic'},
            QsciLexerPython.Number: {'fg': QColor('#098658')},
            QsciLexerPython.Keyword: {'fg': QColor('#0000ff'), 'font_style': 'bold'},
            QsciLexerPython.DoubleQuotedString: {'fg': QColor('#a31515')},
            QsciLexerPython.SingleQuotedString: {'fg': QColor('#a31515')},
            QsciLexerPython.ClassName: {'fg': QColor('#267f99')},
            QsciLexerPython.FunctionMethodName: {'fg': QColor('#795e26')},
            QsciLexerPython.Operator: {'fg': QColor('#000000')},
            QsciLexerPython.Identifier: {'fg': QColor('#001080')},
        },
        'QsciLexerCPP': {
            QsciLexerCPP.Default: {'fg': QColor('#000000')},
            QsciLexerCPP.Comment: {'fg': QColor('#008000'), 'font_style': 'italic'},
            QsciLexerCPP.CommentLine: {'fg': QColor('#008000'), 'font_style': 'italic'},
            QsciLexerCPP.Number: {'fg': QColor('#098658')},
            QsciLexerCPP.Keyword: {'fg': QColor('#0000ff'), 'font_style': 'bold'},
            QsciLexerCPP.DoubleQuotedString: {'fg': QColor('#a31515')},
            QsciLexerCPP.SingleQuotedString: {'fg': QColor('#a31515')},
            QsciLexerCPP.PreProcessor: {'fg': QColor('#9b9b9b')},
        },
        'QsciLexerJavaScript': {
            QsciLexerJavaScript.Default: {'fg': QColor('#000000')},
            QsciLexerJavaScript.Comment: {'fg': QColor('#008000'), 'font_style': 'italic'},
            QsciLexerJavaScript.CommentLine: {'fg': QColor('#008000'), 'font_style': 'italic'},
            QsciLexerJavaScript.Number: {'fg': QColor('#098658')},
            QsciLexerJavaScript.Keyword: {'fg': QColor('#0000ff'), 'font_style': 'bold'},
            QsciLexerJavaScript.DoubleQuotedString: {'fg': QColor('#a31515')},
            QsciLexerJavaScript.SingleQuotedString: {'fg': QColor('#a31515')},
        },
        'QsciLexerHTML': {
            QsciLexerHTML.Default: {'fg': QColor('#000000')},
            QsciLexerHTML.Tag: {'fg': QColor('#800000')},
            QsciLexerHTML.Attribute: {'fg': QColor('#ff0000')},
            QsciLexerHTML.HTMLNumber: {'fg': QColor('#098658')},
            QsciLexerHTML.HTMLDoubleQuotedString: {'fg': QColor('#0000ff')},
            QsciLexerHTML.HTMLSingleQuotedString: {'fg': QColor('#0000ff')},
            QsciLexerHTML.HTMLComment: {'fg': QColor('#808080'), 'font_style': 'italic'},
        },
        'QsciLexerCSS': {
            QsciLexerCSS.Default: {'fg': QColor('#000000')},
            QsciLexerCSS.Tag: {'fg': QColor('#800000')},
            QsciLexerCSS.ClassSelector: {'fg': QColor('#800000')},
            QsciLexerCSS.CSS1Property: {'fg': QColor('#ff0000')},
            QsciLexerCSS.Value: {'fg': QColor('#0000ff')},
            QsciLexerCSS.Comment: {'fg': QColor('#808080'), 'font_style': 'italic'},
        },
        'QsciLexerJava': {
            QsciLexerJava.Default: {'fg': QColor('#000000')},
            QsciLexerJava.Comment: {'fg': QColor('#008000'), 'font_style': 'italic'},
            QsciLexerJava.CommentLine: {'fg': QColor('#008000'), 'font_style': 'italic'},
            QsciLexerJava.Number: {'fg': QColor('#098658')},
            QsciLexerJava.Keyword: {'fg': QColor('#0000ff'), 'font_style': 'bold'},
            QsciLexerJava.DoubleQuotedString: {'fg': QColor('#a31515')},
            QsciLexerJava.SingleQuotedString: {'fg': QColor('#a31515')},
        },
    },
}


def get_app_stylesheet(theme_name):
    t = APP_THEMES.get(theme_name, APP_THEMES['dark'])
    sel = t['selection'].name() if isinstance(t['selection'], QColor) else t['selection']
    return f"""
    QMainWindow {{ background-color: {t['app_bg']}; }}
    QMenuBar {{ background-color: {t['menu_bg']}; color: {t['menu_fg']}; }}
    QMenuBar::item:selected {{ background-color: {sel}; }}
    QMenu {{ background-color: {t['menu_bg']}; color: {t['menu_fg']}; border: 1px solid #454545; }}
    QMenu::item:selected {{ background-color: {sel}; }}
    QToolBar {{ background-color: {t['toolbar_bg']}; border: none; spacing: 4px; }}
    QStatusBar {{ background-color: {t['statusbar_bg']}; color: {t['statusbar_fg']}; }}
    QTabWidget::pane {{ border: none; background-color: {t['app_bg']}; }}
    QTabBar::tab {{ background-color: {t['tab_bg']}; color: {t['tab_fg']}; padding: 6px 16px; border: none; }}
    QTabBar::tab:selected {{ background-color: {t['tab_active_bg']}; color: {t['tab_active_fg']}; }}
    QTabBar::tab:hover {{ background-color: {sel}; }}
    QLabel {{ color: {t['app_fg']}; }}
    """
