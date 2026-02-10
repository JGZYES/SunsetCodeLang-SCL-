# Time plugin for SunsetCodeLang

import time

class TimePlugin:
    def __init__(self, interpreter):
        self.interpreter = interpreter
    
    def register_syntax(self):
        """Register time syntax handlers"""
        pass
    
    def parse_statement(self, tokens, pos):
        """Parse time-related statements"""
        # Create local variables for parsing
        local_pos = pos
        
        def peek(offset=0):
            if local_pos + offset < len(tokens):
                return tokens[local_pos + offset]
            return None
        
        def consume():
            nonlocal local_pos
            if local_pos < len(tokens):
                token = tokens[local_pos]
                local_pos += 1
                return token
            return None
        
        token = peek()
        if not token:
            return None, pos
        
        if token[0] == 'IDENTIFIER' and token[1] == 'time':
            # Time statement: time : now
            consume()  # Consume 'time'
            if peek() and peek()[0] == 'ASSIGN':
                consume()  # Consume ':'
                sub_token = peek()
                if sub_token and sub_token[0] == 'IDENTIFIER' and sub_token[1] == 'now':
                    consume()  # Consume 'now'
                    return ('TIME_NOW',), local_pos
        
        return None, pos
    
    def execute_statement(self, stmt):
        """Execute time-related statements"""
        if stmt[0] == 'TIME_NOW':
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"Current time: {current_time}")
            return True
        return False
