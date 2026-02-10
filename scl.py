#!/usr/bin/env python3
"""
SunsetCodeLang (SCL) Interpreter
Main interpreter for the SCL language
"""

import sys
import os
import re
import importlib.util

class SCLInterpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.plugins = {}
        self.loaded_plugins = set()
    
    def load_plugin(self, plugin_path):
        """Load a plugin from the given path"""
        try:
            # Convert plugin path to module path
            # e.g., other>time becomes plugins.other.time
            module_name = plugin_path.replace('>', '.')
            full_module_name = f'plugins.{module_name}'
            
            # Check if plugin is already loaded
            if full_module_name in self.loaded_plugins:
                return True
            
            # Create plugin file path
            plugin_file = os.path.join('plugins', plugin_path.replace('>', os.sep) + '.py')
            
            if not os.path.exists(plugin_file):
                print(f"Error: Plugin {plugin_path} not found at {plugin_file}")
                return False
            
            # Load the plugin module
            spec = importlib.util.spec_from_file_location(full_module_name, plugin_file)
            plugin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin_module)
            
            # Create plugin instance
            plugin_class = getattr(plugin_module, f'{plugin_path.split(">")[-1].capitalize()}Plugin', None)
            if not plugin_class:
                print(f"Error: Plugin {plugin_path} does not have a proper plugin class")
                return False
            
            plugin_instance = plugin_class(self)
            self.plugins[plugin_path] = plugin_instance
            self.loaded_plugins.add(full_module_name)
            
            # Register syntax handlers
            if hasattr(plugin_instance, 'register_syntax'):
                plugin_instance.register_syntax()
            
            return True
        except Exception as e:
            print(f"Error loading plugin {plugin_path}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def tokenize(self, code):
        """Tokenize the SCL code"""
        tokens = []
        code = code.strip()
        i = 0
        n = len(code)
        
        while i < n:
            # Skip whitespace
            while i < n and code[i].isspace():
                i += 1
            
            if i >= n:
                break
            
            char = code[i]
            
            # String literal
            if char == '"':
                j = i + 1
                while j < n and code[j] != '"':
                    j += 1
                if j < n:
                    tokens.append(('STRING', code[i+1:j]))
                    i = j + 1
                else:
                    tokens.append(('STRING', code[i+1:]))
                    i = n
            
            # Number literal
            elif char.isdigit():
                j = i
                while j < n and (code[j].isdigit() or code[j] == '.'):
                    j += 1
                tokens.append(('NUMBER', code[i:j]))
                i = j
            
            # Identifier
            elif char.isalpha() or char == '_':
                j = i
                while j < n and (code[j].isalnum() or code[j] == '_'):
                    j += 1
                tokens.append(('IDENTIFIER', code[i:j]))
                i = j
            
            # Separator
            elif char == '|':
                tokens.append(('SEPARATOR', char))
                i += 1
            
            # Assignment
            elif char == ':':
                tokens.append(('ASSIGN', char))
                i += 1
            
            # Operator
            elif char in '+-*/=<>!&|':
                j = i
                while j < n and code[j] in '+-*/=<>!&|':
                    j += 1
                tokens.append(('OPERATOR', code[i:j]))
                i = j
            
            # Parentheses
            elif char in '()[]{}':
                tokens.append(('PAREN', char))
                i += 1
            
            # Comment
            elif char == '#':
                j = i
                while j < n and code[j] != '\n':
                    j += 1
                tokens.append(('COMMENT', code[i:j]))
                i = j
            
            # Unknown character
            else:
                tokens.append(('UNKNOWN', char))
                i += 1
        
        return tokens
    
    def parse_expression(self, tokens, pos):
        """Parse an expression from the tokens"""
        # Simple expression parser
        # This is a very basic parser, just for demonstration
        if pos >= len(tokens):
            return None, pos
        
        token = tokens[pos]
        if token[0] == 'STRING' or token[0] == 'NUMBER':
            return token, pos + 1
        elif token[0] == 'IDENTIFIER':
            return token, pos + 1
        elif token[0] == 'PAREN' and token[1] == '(':
            expr, pos = self.parse_expression(tokens, pos + 1)
            if pos < len(tokens) and tokens[pos][0] == 'PAREN' and tokens[pos][1] == ')':
                return expr, pos + 1
            return None, pos
        return None, pos
    
    def parse_statement(self, tokens, pos):
        """Parse a statement from the tokens"""
        for plugin_name, plugin in self.plugins.items():
            if hasattr(plugin, 'parse_statement'):
                stmt, new_pos = plugin.parse_statement(tokens, pos)
                if stmt:
                    return stmt, new_pos
        return None, pos
    
    def evaluate_expression(self, expr):
        """Evaluate an expression"""
        if expr[0] == 'STRING':
            return expr[1]
        elif expr[0] == 'NUMBER':
            try:
                if '.' in expr[1]:
                    return float(expr[1])
                else:
                    return int(expr[1])
            except:
                return 0
        elif expr[0] == 'IDENTIFIER':
            return self.variables.get(expr[1], 0)
        return 0
    
    def execute_statement(self, stmt):
        """Execute a statement"""
        for plugin_name, plugin in self.plugins.items():
            if hasattr(plugin, 'execute_statement'):
                if plugin.execute_statement(stmt):
                    return True
        return False
    
    def execute(self, code, file_path=None):
        """Execute the given SCL code"""
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Handle plugin imports
            if line.startswith('simp{') and line.endswith('}'):
                plugin_path = line[5:-1].strip()
                if not self.load_plugin(plugin_path):
                    print(f"Error at line {line_num}: Failed to load plugin {plugin_path}")
                    print(f"Code: {line}")
                    return False
                continue
            
            try:
                tokens = self.tokenize(line)
                if tokens:
                    stmt, _ = self.parse_statement(tokens, 0)
                    if stmt:
                        if not self.execute_statement(stmt):
                            print(f"Error at line {line_num}: Failed to execute statement")
                            print(f"Code: {line}")
                            return False
                    else:
                        print(f"Error at line {line_num}: Invalid syntax")
                        print(f"Code: {line}")
                        return False
            except Exception as e:
                print(f"Error at line {line_num}: {e}")
                print(f"Code: {line}")
                import traceback
                traceback.print_exc()
                return False
        
        return True

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python scl.py <file.scl>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        sys.exit(1)
    
    interpreter = SCLInterpreter()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        success = interpreter.execute(code, file_path)
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"Error executing file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
