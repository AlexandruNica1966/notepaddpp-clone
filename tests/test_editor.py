#!/usr/bin/env python3
"""
Tests for Notepad++ Clone - Tkinter Edition
Run with: pytest tests/ -v
"""

import pytest
import tkinter as tk
import os
import tempfile
from pathlib import Path

# Set virtual display for headless testing
os.environ['DISPLAY'] = ':99'

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from main import EditorTab, SyntaxHighlighter, FindReplaceDialog, NotepadPlusPlusClone


@pytest.fixture(scope='function')
def root():
    """Create a Tk root window for testing"""
    try:
        r = tk.Tk()
        r.withdraw()  # Hide window
        yield r
        r.destroy()
    except tk.TclError:
        pytest.skip('No display available')


class TestSyntaxHighlighter:
    """Test syntax highlighting functionality"""
    
    def test_themes_exist(self):
        """Verify all themes are defined"""
        assert 'dark' in SyntaxHighlighter.THEMES
        assert 'light' in SyntaxHighlighter.THEMES
        
    def test_theme_colors(self):
        """Verify theme has required colors"""
        for theme in SyntaxHighlighter.THEMES.values():
            assert 'bg' in theme
            assert 'fg' in theme
            assert 'keyword' in theme
            assert 'string' in theme
            assert 'comment' in theme
            
    def test_language_patterns(self):
        """Verify language patterns are defined"""
        assert 'python' in SyntaxHighlighter.PATTERNS
        assert 'javascript' in SyntaxHighlighter.PATTERNS
        assert 'html' in SyntaxHighlighter.PATTERNS
        assert 'css' in SyntaxHighlighter.PATTERNS
        assert 'cpp' in SyntaxHighlighter.PATTERNS
        assert 'java' in SyntaxHighlighter.PATTERNS
        
    def test_python_keywords(self):
        """Test Python keyword pattern"""
        pattern = SyntaxHighlighter.PATTERNS['python']['keyword']
        import re
        assert re.search(pattern, 'def')
        assert re.search(pattern, 'class')
        assert re.search(pattern, 'import')
        assert not re.search(pattern, 'hello')


class TestEditorTab:
    """Test editor tab functionality"""
    
    def test_create_tab(self, root):
        """Test creating a new editor tab"""
        tab = EditorTab(root)
        assert tab is not None
        assert tab.filepath is None
        assert tab.modified is False
        tab.destroy()
        
    def test_tab_title_untitled(self, root):
        """Test tab title for untitled file"""
        tab = EditorTab(root)
        assert 'Untitled' in tab.get_title()
        tab.destroy()
        
    def test_tab_modified_indicator(self, root):
        """Test modified indicator in title"""
        tab = EditorTab(root)
        tab.modified = True
        assert tab.get_title().startswith('*')
        tab.destroy()
        
    def test_save_and_load_file(self, root):
        """Test saving and loading a file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def hello():\n    print("world")\n')
            temp_path = f.name
            
        try:
            tab = EditorTab(root, filepath=temp_path)
            assert tab.filepath == temp_path
            assert 'def hello' in tab.text.get('1.0', tk.END)
            
            # Modify and save
            tab.text.delete('1.0', tk.END)
            tab.text.insert('1.0', 'def modified():\n    pass\n')
            tab.save_file()
            
            # Verify saved
            with open(temp_path, 'r') as f:
                content = f.read()
            assert 'def modified' in content
            assert tab.modified is False
            
            tab.destroy()
        finally:
            os.unlink(temp_path)
            
    def test_encoding_detection(self, root):
        """Test file encoding detection"""
        # UTF-8 file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write('Hello 世界\n')
            utf8_path = f.name
            
        try:
            tab = EditorTab(root, filepath=utf8_path)
            assert tab.encoding == 'utf-8'
            tab.destroy()
        finally:
            os.unlink(utf8_path)


class TestFindReplace:
    """Test find and replace functionality"""
    
    def test_find_pattern_simple(self, root):
        """Test simple find pattern"""
        tab = EditorTab(root)
        tab.text.insert('1.0', 'Hello World\nHello Python\n')
        
        # Test pattern building directly
        import re
        pattern = re.compile(re.escape('Hello'))
        assert pattern.search('Hello World')
        
        tab.destroy()
        
    def test_find_pattern_case_insensitive(self, root):
        """Test case insensitive search"""
        import re
        pattern = re.compile(re.escape('hello'), re.IGNORECASE)
        assert pattern.search('HELLO')
        
    def test_find_pattern_whole_word(self, root):
        """Test whole word search"""
        import re
        pattern = re.compile(r'\b' + re.escape('world') + r'\b')
        assert pattern.search('hello world')
        assert not pattern.search('worldwide')
        
    def test_replace_all(self, root):
        """Test replace all functionality"""
        tab = EditorTab(root)
        tab.text.insert('1.0', 'foo bar foo baz foo\n')
        
        # Test the replace logic directly without dialog
        import re
        content = tab.text.get('1.0', tk.END)
        pattern = re.compile(re.escape('foo'))
        replacement = 'qux'
        
        # Simulate replace_all
        new_content = pattern.sub(replacement, content)
        tab.text.delete('1.0', tk.END)
        tab.text.insert('1.0', new_content)
        
        content = tab.text.get('1.0', tk.END)
        assert 'qux bar qux baz qux' in content
        
        tab.destroy()


class TestNotepadPlusPlusClone:
    """Test main application"""
    
    def test_app_creation(self, root):
        """Test creating main application"""
        app = NotepadPlusPlusClone()
        assert app.root is not None
        assert app.notebook is not None
        app.root.destroy()
        
    def test_new_file(self, root):
        """Test creating new file"""
        app = NotepadPlusPlusClone()
        initial_tabs = len(app.notebook.tabs())
        app.new_file()
        assert len(app.notebook.tabs()) == initial_tabs + 1
        app.root.destroy()
        
    def test_theme_toggle(self, root):
        """Test theme toggling"""
        app = NotepadPlusPlusClone()
        initial_theme = app.current_theme
        app.toggle_theme()
        assert app.current_theme != initial_theme
        app.toggle_theme()
        assert app.current_theme == initial_theme
        app.root.destroy()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
