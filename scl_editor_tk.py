#!/usr/bin/env python3
"""
SunsetCodeLang Editor (Tkinter version)
A code editor for SCL language using Tkinter
"""

import sys
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import scrolledtext
import re
import subprocess
import importlib.util

def extract_keywords_from_plugin(plugin_file):
    """Extract syntax keywords from a plugin file"""
    keywords = set()
    try:
        with open(plugin_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all IDENTIFIER checks in parse_statement method
        # Pattern: token[1] == 'keyword'
        pattern = r"token\[1\]\s*==\s*['\"]([^'\"]+)['\"]"
        matches = re.findall(pattern, content)
        keywords.update(matches)
        
        # Also find IDENTIFIER checks with peek
        # Pattern: peek()[1] == 'keyword'
        pattern2 = r"peek\(\)\[1\]\s*==\s*['\"]([^'\"]+)['\"]"
        matches2 = re.findall(pattern2, content)
        keywords.update(matches2)
        
        # Find sub_token checks
        # Pattern: sub_token[1] == 'keyword'
        pattern3 = r"sub_token\[1\]\s*==\s*['\"]([^'\"]+)['\"]"
        matches3 = re.findall(pattern3, content)
        keywords.update(matches3)
        
        # Find next_token checks
        # Pattern: next_token[1] == 'keyword'
        pattern4 = r"next_token\[1\]\s*==\s*['\"]([^'\"]+)['\"]"
        matches4 = re.findall(pattern4, content)
        keywords.update(matches4)
        
    except Exception as e:
        print(f"Error extracting keywords from {plugin_file}: {e}")
    
    return keywords

def get_all_plugin_keywords():
    """Get all syntax keywords from all plugins"""
    keywords = set()
    plugins_dir = 'plugins'
    
    if not os.path.exists(plugins_dir):
        return keywords
    
    # Walk through the plugins directory
    for root, dirs, files in os.walk(plugins_dir):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                plugin_file = os.path.join(root, file)
                plugin_keywords = extract_keywords_from_plugin(plugin_file)
                keywords.update(plugin_keywords)
    
    return keywords

class SCLLexer:
    """Syntax highlighter for SunsetCodeLang"""
    
    def __init__(self, text_widget, keywords=None):
        self.text = text_widget
        self.keywords = keywords if keywords else []
        self.text.tag_configure("keyword", foreground="purple", font=("Consolas", 11, "bold"))
        self.text.tag_configure("string", foreground="green")
        self.text.tag_configure("comment", foreground="gray")
        self.text.tag_configure("operator", foreground="blue")
        self.text.tag_configure("number", foreground="red")
    
    def update_keywords(self, keywords):
        """Update the keywords list for highlighting"""
        self.keywords = keywords
        self.highlight()
    
    def highlight(self, event=None):
        """Apply syntax highlighting to the entire text"""
        # Clear all existing tags
        for tag in ["keyword", "string", "comment", "operator", "number"]:
            self.text.tag_remove(tag, "1.0", tk.END)
        
        # Highlight keywords from plugins
        for keyword in self.keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            start = "1.0"
            while True:
                start = self.text.search(pattern, start, stopindex=tk.END, regexp=True)
                if not start:
                    break
                end = f"{start}+{len(keyword)}c"
                self.text.tag_add("keyword", start, end)
                start = end
        
        # Highlight strings
        start = "1.0"
        while True:
            start = self.text.search(r'"[^"]*"', start, stopindex=tk.END, regexp=True)
            if not start:
                break
            # Get the matched string
            matched = self.text.get(start, f"{start}+100c")
            quote_pos = matched.find('"', 1)
            if quote_pos == -1:
                start = f"{start}+1c"
                continue
            end = f"{start}+{quote_pos+1}c"
            self.text.tag_add("string", start, end)
            start = end
        
        # Highlight comments
        start = "1.0"
        while True:
            start = self.text.search(r'#.*', start, stopindex=tk.END, regexp=True)
            if not start:
                break
            # Get the line number
            line_num = int(start.split('.')[0])
            # Get the end of the line
            end = f"{line_num}.end"
            self.text.tag_add("comment", start, end)
            # Move to the next line
            start = f"{line_num + 1}.0"
        
        # Highlight operators
        operators = ["+", "*", "|", ":"]
        for op in operators:
            pattern = re.escape(op)
            start = "1.0"
            while True:
                start = self.text.search(pattern, start, stopindex=tk.END, regexp=True)
                if not start:
                    break
                end = f"{start}+1c"
                self.text.tag_add("operator", start, end)
                start = end
        
        # Highlight numbers
        start = "1.0"
        while True:
            start = self.text.search(r'\b\d+\b', start, stopindex=tk.END, regexp=True)
            if not start:
                break
            # Get the matched number
            matched = self.text.get(start, f"{start}+20c")
            num_end = 0
            while num_end < len(matched) and matched[num_end].isdigit():
                num_end += 1
            end = f"{start}+{num_end}c"
            self.text.tag_add("number", start, end)
            start = end

class SCLEditor(tk.Tk):
    """Main editor window"""
    
    def __init__(self):
        super().__init__()
        self.title("SunsetCodeLang Editor")
        self.geometry("800x600")
        self.current_file = None
        
        # Get all plugin keywords for syntax highlighting
        self.plugin_keywords = list(get_all_plugin_keywords())
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create the UI widgets"""
        # Create menu bar
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.close)
        
        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run", command=self.run_code, accelerator="F5")
        
        # Create toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, side=tk.TOP)
        
        # Toolbar buttons
        open_btn = ttk.Button(toolbar, text="Open", command=self.open_file)
        open_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        save_btn = ttk.Button(toolbar, text="Save", command=self.save_file)
        save_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        run_btn = ttk.Button(toolbar, text="Run", command=self.run_code)
        run_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Create paned window for editor and console
        self.paned_window = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create text editor
        self.editor = scrolledtext.ScrolledText(self.paned_window, font=("Consolas", 11), wrap=tk.WORD)
        self.paned_window.add(self.editor, weight=3)
        
        # Create console
        console_frame = ttk.LabelFrame(self.paned_window, text="Console Output")
        self.console = scrolledtext.ScrolledText(console_frame, font=("Consolas", 10), wrap=tk.WORD)
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.console.config(state=tk.DISABLED)  # Make console read-only
        self.paned_window.add(console_frame, weight=1)
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Create syntax highlighter with plugin keywords
        self.highlighter = SCLLexer(self.editor, keywords=self.plugin_keywords)
        
        # Bind keyboard shortcuts
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<F5>", lambda e: self.run_code())
        
        # Bind text change event to update syntax highlighting
        self.editor.bind("<KeyRelease>", self.on_text_change)
        
        # Set tab width
        self.editor.config(tabs=(4,))
    
    def on_text_change(self, event=None):
        """Handle text change events"""
        # Get current content
        content = self.editor.get("1.0", tk.END)
        
        # Update syntax highlighting based on plugins used
        self.update_syntax_highlighting(content)
    
    def open_file(self):
        """Open a file"""
        filetypes = [(".scl files", "*.scl"), ("All files", "*")]
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.editor.delete("1.0", tk.END)
                self.editor.insert("1.0", content)
                self.current_file = file_path
                self.title(f"SunsetCodeLang Editor - {os.path.basename(file_path)}")
                self.status_var.set(f"Opened: {file_path}")
                
                # Update syntax highlighting based on plugins used in the file
                self.update_syntax_highlighting(content)
                
                self.highlighter.highlight()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")
    
    def update_syntax_highlighting(self, content):
        """Update syntax highlighting based on plugins used in the file"""
        # Extract plugin imports from the file
        plugin_imports = re.findall(r'simp\{([^}]+)\}', content)
        
        # Get all keywords from imported plugins
        keywords = set()
        
        # Always include basic keywords
        keywords.update(['set', 'sout', 'sif', 'selif', 'sle', 'simp'])
        
        # Add keywords from imported plugins
        for plugin_import in plugin_imports:
            plugin_path = plugin_import.replace('>', os.sep)
            plugin_file = os.path.join('plugins', plugin_path + '.py')
            
            if os.path.exists(plugin_file):
                plugin_keywords = extract_keywords_from_plugin(plugin_file)
                keywords.update(plugin_keywords)
        
        # Update the highlighter with the new keywords
        self.highlighter.update_keywords(list(keywords))
    
    def save_file(self):
        """Save the current file"""
        if self.current_file:
            try:
                content = self.editor.get("1.0", tk.END)
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(content)
                self.status_var.set(f"Saved: {self.current_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
        else:
            self.save_as_file()
    
    def save_as_file(self):
        """Save the current file with a new name"""
        filetypes = [(".scl files", "*.scl"), ("All files", "*")]
        file_path = filedialog.asksaveasfilename(
            defaultextension=".scl",
            filetypes=filetypes
        )
        
        if file_path:
            try:
                content = self.editor.get("1.0", tk.END)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.current_file = file_path
                self.title(f"SunsetCodeLang Editor - {os.path.basename(file_path)}")
                self.status_var.set(f"Saved: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")
    
    def run_code(self):
        """Run the current SCL code"""
        if not self.current_file:
            # Save the file first
            self.save_as_file()
        
        if self.current_file:
            try:
                # Clear console
                self.console.config(state=tk.NORMAL)
                self.console.delete("1.0", tk.END)
                self.console.insert(tk.END, "Executing code...\n\n")
                self.console.config(state=tk.DISABLED)
                
                # Run the SCL code using the interpreter
                result = subprocess.run(
                    [sys.executable, "scl.py", self.current_file],
                    capture_output=True,
                    text=True,
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )
                
                # Show the output in console
                output = result.stdout
                error = result.stderr
                
                self.console.config(state=tk.NORMAL)
                if error:
                    self.console.insert(tk.END, "Runtime Error:\n")
                    self.console.insert(tk.END, error)
                elif "Error at line" in output:
                    self.console.insert(tk.END, "Runtime Error:\n")
                    self.console.insert(tk.END, output)
                else:
                    self.console.insert(tk.END, "Execution Result:\n")
                    self.console.insert(tk.END, output)
                self.console.config(state=tk.DISABLED)
                
                self.status_var.set("Code executed")
            except Exception as e:
                self.console.config(state=tk.NORMAL)
                self.console.insert(tk.END, f"Failed to run code: {e}\n")
                self.console.config(state=tk.DISABLED)
                messagebox.showerror("Error", f"Failed to run code: {e}")
    
    def close(self):
        """Close the editor"""
        # Check if the file has been modified
        if self.editor.edit_modified() and self.current_file:
            response = messagebox.askyesnocancel(
                "Save Changes",
                "Do you want to save changes to the file?"
            )
            
            if response is None:
                return  # Cancel
            elif response:
                self.save_file()
        
        self.destroy()
    
    def on_closing(self):
        """Handle window closing event"""
        self.close()

if __name__ == "__main__":
    editor = SCLEditor()
    editor.protocol("WM_DELETE_WINDOW", editor.on_closing)
    editor.mainloop()
