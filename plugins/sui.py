# SUI (SunsetCodeLang UI) plugin
# Uses tkinter to create graphical user interfaces

import tkinter as tk
from tkinter import Canvas
import time

class SuiPlugin:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.windows = {}
        self.running_windows = {}
    
    def register_syntax(self):
        """Register SUI syntax handlers"""
        pass
    
    def parse_statement(self, tokens, pos):
        """Parse SUI statements"""
        interpreter = self.interpreter
        interpreter.tokens = tokens
        interpreter.pos = pos
        
        def peek(offset=0):
            if interpreter.pos + offset < len(interpreter.tokens):
                return interpreter.tokens[interpreter.pos + offset]
            return None
        
        def consume():
            if interpreter.pos < len(interpreter.tokens):
                token = interpreter.tokens[interpreter.pos]
                interpreter.pos += 1
                return token
            return None
        
        token = peek()
        if not token:
            return None, pos
        
        if token[0] == 'IDENTIFIER' and token[1] == 'sui':
            consume()  # Consume 'sui'
            
            next_token = peek()
            if not next_token:
                return None, pos
            
            # sui create : window_name
            if next_token[0] == 'IDENTIFIER' and next_token[1] == 'create':
                consume()  # Consume 'create'
                if peek() and peek()[0] == 'ASSIGN':
                    consume()  # Consume ':'
                    window_name = consume()[1]  # Get window name
                    return ('SUI_CREATE', window_name), interpreter.pos
            
            # sui run window_name
            elif next_token[0] == 'IDENTIFIER' and next_token[1] == 'run':
                consume()  # Consume 'run'
                window_name = consume()[1]  # Get window name
                return ('SUI_RUN', window_name), interpreter.pos
            
            # sui set window_name : width : height
            elif next_token[0] == 'IDENTIFIER' and next_token[1] == 'set':
                consume()  # Consume 'set'
                window_name = consume()[1]  # Get window name
                if peek() and peek()[0] == 'ASSIGN':
                    consume()  # Consume ':'
                    width = consume()[1]  # Get width
                    if peek() and peek()[0] == 'ASSIGN':
                        consume()  # Consume ':'
                        height = consume()[1]  # Get height
                        return ('SUI_SET_SIZE', window_name, width, height), interpreter.pos
            
            # sui del window_name
            elif next_token[0] == 'IDENTIFIER' and next_token[1] == 'del':
                consume()  # Consume 'del'
                window_name = consume()[1]  # Get window name
                return ('SUI_DELETE', window_name), interpreter.pos
            
            # sui icon : icon_path
            elif next_token[0] == 'IDENTIFIER' and next_token[1] == 'icon':
                consume()  # Consume 'icon'
                if peek() and peek()[0] == 'ASSIGN':
                    consume()  # Consume ':'
                    icon_path = consume()[1]  # Get icon path
                    return ('SUI_SET_ICON', icon_path), interpreter.pos
            
            # sui shape : x : y : color
            elif next_token[0] == 'IDENTIFIER':
                shape = next_token[1]  # Get shape name
                consume()  # Consume shape name
                if peek() and peek()[0] == 'ASSIGN':
                    consume()  # Consume ':'
                    x = consume()[1]  # Get x coordinate
                    if peek() and peek()[0] == 'ASSIGN':
                        consume()  # Consume ':'
                        y = consume()[1]  # Get y coordinate
                        if peek() and peek()[0] == 'ASSIGN':
                            consume()  # Consume ':'
                            color = consume()[1]  # Get color
                            return ('SUI_DRAW', shape, x, y, color), interpreter.pos
        
        return None, pos
    
    def execute_statement(self, stmt):
        """Execute SUI statements"""
        if stmt[0] == 'SUI_CREATE':
            window_name = stmt[1]
            try:
                # Create window
                window = tk.Tk()
                window.title(window_name)
                window.geometry("400x300")
                
                # Create canvas for drawing
                canvas = Canvas(window, width=400, height=300, bg="white")
                canvas.pack(fill=tk.BOTH, expand=True)
                
                self.windows[window_name] = {"window": window, "canvas": canvas}
                print(f"Window '{window_name}' created")
            except Exception as e:
                print(f"Error creating window: {e}")
            return True
        
        elif stmt[0] == 'SUI_SET_SIZE':
            window_name, width, height = stmt[1], stmt[2], stmt[3]
            try:
                if window_name in self.windows:
                    window = self.windows[window_name]["window"]
                    geometry = f"{width}x{height}"
                    window.geometry(geometry)
                    
                    # Update canvas size
                    canvas = self.windows[window_name]["canvas"]
                    canvas.config(width=width, height=height)
                    
                    print(f"Window '{window_name}' size set to {width}x{height}")
                else:
                    print(f"Window '{window_name}' not found")
            except Exception as e:
                print(f"Error setting window size: {e}")
            return True
        
        elif stmt[0] == 'SUI_RUN':
            window_name = stmt[1]
            try:
                if window_name in self.windows:
                    window = self.windows[window_name]["window"]
                    # Run window in a blocking way to keep it open
                    # This will run until the window is closed
                    print(f"Window '{window_name}' running (blocking)")
                    
                    # Set a protocol to handle window closing
                    def on_closing():
                        if window_name in self.running_windows:
                            del self.running_windows[window_name]
                        if window_name in self.windows:
                            del self.windows[window_name]
                        try:
                            window.destroy()
                        except:
                            pass
                    
                    window.protocol("WM_DELETE_WINDOW", on_closing)
                    
                    # Enter the main loop
                    self.running_windows[window_name] = True
                    
                    # Use a simple loop to keep the window open
                    while window_name in self.running_windows:
                        try:
                            window.update()
                            import time
                            time.sleep(0.01)
                        except:
                            if window_name in self.running_windows:
                                del self.running_windows[window_name]
                            break
                else:
                    print(f"Window '{window_name}' not found")
            except Exception as e:
                print(f"Error running window: {e}")
                if window_name in self.running_windows:
                    del self.running_windows[window_name]
            return True
        
        elif stmt[0] == 'SUI_DELETE':
            window_name = stmt[1]
            try:
                if window_name in self.windows:
                    window = self.windows[window_name]["window"]
                    window.destroy()
                    del self.windows[window_name]
                    if window_name in self.running_windows:
                        del self.running_windows[window_name]
                    print(f"Window '{window_name}' deleted")
                else:
                    print(f"Window '{window_name}' not found")
            except Exception as e:
                print(f"Error deleting window: {e}")
            return True
        
        elif stmt[0] == 'SUI_SET_ICON':
            icon_path = stmt[1]
            try:
                if self.windows:
                    # Get the first window (you can modify this to target specific windows)
                    window_name = next(iter(self.windows))
                    window = self.windows[window_name]["window"]
                    # Set window icon
                    try:
                        window.iconbitmap(icon_path)
                        print(f"Window '{window_name}' icon set to: {icon_path}")
                    except Exception as e:
                        print(f"Error setting window icon: {e}")
                else:
                    print("No windows available to set icon")
            except Exception as e:
                print(f"Error setting window icon: {e}")
            return True
        
        elif stmt[0] == 'SUI_DRAW':
            shape, x, y, color = stmt[1], stmt[2], stmt[3], stmt[4]
            try:
                # Draw on the last created window or a specific window
                # For simplicity, draw on the first available window
                if self.windows:
                    # Get the first window (you can modify this to target specific windows)
                    window_name = next(iter(self.windows))
                    canvas = self.windows[window_name]["canvas"]
                    
                    x_val = int(x)
                    y_val = int(y)
                    
                    # Draw different shapes
                    if shape == 'circle':
                        # Draw circle (oval)
                        radius = 20
                        canvas.create_oval(
                            x_val - radius, y_val - radius,
                            x_val + radius, y_val + radius,
                            fill=color
                        )
                    elif shape == 'rectangle':
                        # Draw rectangle
                        size = 40
                        canvas.create_rectangle(
                            x_val - size/2, y_val - size/2,
                            x_val + size/2, y_val + size/2,
                            fill=color
                        )
                    elif shape == 'line':
                        # Draw line (from x,y to x+50,y+50)
                        canvas.create_line(
                            x_val, y_val,
                            x_val + 50, y_val + 50,
                            fill=color, width=2
                        )
                    else:
                        print(f"Unknown shape: {shape}")
                    
                    print(f"Drew {shape} at ({x},{y}) with color {color}")
                else:
                    print("No windows available to draw on")
            except Exception as e:
                print(f"Error drawing shape: {e}")
            return True
        
        return False
