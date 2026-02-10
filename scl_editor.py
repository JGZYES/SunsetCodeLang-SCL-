#!/usr/bin/env python3
"""
SunsetCodeLang Editor
A code editor for SCL language using PyQt5
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QAction, QFileDialog,
    QToolBar, QMessageBox, QStatusBar, QMenuBar, QMenu, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel
)
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor
from PyQt5.QtCore import Qt, QRegExp

class SCLLexer(QSyntaxHighlighter):
    """Syntax highlighter for SunsetCodeLang"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Define syntax highlighting rules
        self.highlighting_rules = []
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(128, 0, 128))  # Purple
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "set", "sout", "sif", "selif", "sle", "simp"
        ]
        for keyword in keywords:
            pattern = QRegExp(r'\\b' + keyword + r'\\b')
            self.highlighting_rules.append((pattern, keyword_format))
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(0, 128, 0))  # Green
        pattern = QRegExp(r'"[^"]*"')
        pattern.setMinimal(True)
        self.highlighting_rules.append((pattern, string_format))
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(128, 128, 128))  # Gray
        pattern = QRegExp(r'#.*')
        self.highlighting_rules.append((pattern, comment_format))
        
        # Operators
        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor(0, 0, 255))  # Blue
        operators = ["+", "*", "|", ":"]
        for operator in operators:
            pattern = QRegExp(re.escape(operator))
            self.highlighting_rules.append((pattern, operator_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(255, 0, 0))  # Red
        pattern = QRegExp(r'\\b\d+\\b')
        self.highlighting_rules.append((pattern, number_format))
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text"""
        for pattern, format in self.highlighting_rules:
            regex = QRegExp(pattern)
            index = regex.indexIn(text)
            while index >= 0:
                length = regex.matchedLength()
                self.setFormat(index, length, format)
                index = regex.indexIn(text, index + length)

class SCLEditor(QMainWindow):
    """Main editor window"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.current_file = None
    
    def init_ui(self):
        """Initialize the user interface"""
        # Set window properties
        self.setWindowTitle("SunsetCodeLang Editor")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Create actions
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        save_as_action = QAction("Save As", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_as_file)
        toolbar.addAction(save_as_action)
        
        toolbar.addSeparator()
        
        run_action = QAction("Run", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.run_code)
        toolbar.addAction(run_action)
        
        # Create text editor
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Consolas", 11))
        self.editor.setTabStopWidth(4)
        layout.addWidget(self.editor)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Create syntax highlighter
        self.highlighter = SCLLexer(self.editor.document())
        
        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Run menu
        run_menu = menubar.addMenu("Run")
        run_menu.addAction(run_action)
    
    def open_file(self):
        """Open a file"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open SCL File", "", "SCL Files (*.scl);;All Files (*)", options=options
        )
        
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.editor.setPlainText(content)
                self.current_file = file_name
                self.setWindowTitle(f"SunsetCodeLang Editor - {os.path.basename(file_name)}")
                self.status_bar.showMessage(f"Opened: {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")
    
    def save_file(self):
        """Save the current file"""
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                self.status_bar.showMessage(f"Saved: {self.current_file}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
        else:
            self.save_as_file()
    
    def save_as_file(self):
        """Save the current file with a new name"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save As", "", "SCL Files (*.scl);;All Files (*)", options=options
        )
        
        if file_name:
            # Ensure the file has .scl extension
            if not file_name.endswith('.scl'):
                file_name += '.scl'
            
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
                self.current_file = file_name
                self.setWindowTitle(f"SunsetCodeLang Editor - {os.path.basename(file_name)}")
                self.status_bar.showMessage(f"Saved: {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
    
    def run_code(self):
        """Run the current SCL code"""
        if not self.current_file:
            # Save the file first
            self.save_as_file()
        
        if self.current_file:
            try:
                # Run the SCL code using the interpreter
                import subprocess
                result = subprocess.run(
                    [sys.executable, "scl.py", self.current_file],
                    capture_output=True,
                    text=True,
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )
                
                # Show the output
                output = result.stdout
                error = result.stderr
                
                if error:
                    QMessageBox.critical(self, "Error", f"Runtime Error:\n{error}")
                else:
                    QMessageBox.information(self, "Output", f"Execution Result:\n{output}")
                
                self.status_bar.showMessage("Code executed")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to run code: {str(e)}")
    
    def closeEvent(self, event):
        """Handle close event"""
        # Check if the file has been modified
        if self.editor.document().isModified() and self.current_file:
            reply = QMessageBox.question(
                self, "Save Changes",
                "Do you want to save changes to the file?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.save_file()
                event.accept()
            elif reply == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = SCLEditor()
    editor.show()
    sys.exit(app.exec_())
