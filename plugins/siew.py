# Siew plugin for SunsetCodeLang
# Enhanced syntax with improved if/while statements

class SiewPlugin:
    def __init__(self, interpreter):
        self.interpreter = interpreter
    
    def register_syntax(self):
        """Register enhanced syntax handlers"""
        pass
    
    def parse_statement(self, tokens, pos):
        """Parse enhanced statements"""
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
        
        # swhile statement: swhile condition {
        #                      ...
        #                   }
        if token[0] == 'IDENTIFIER' and token[1] == 'swhile':
            consume()  # Consume 'swhile'
            condition, _ = self.interpreter.parse_expression(interpreter.tokens, interpreter.pos)
            if condition and peek() and peek()[0] == 'LEFT_BRACE':
                consume()  # Consume '{'
                body = []
                # Parse body statements until '}'
                while peek() and not (peek()[0] == 'RIGHT_BRACE'):
                    stmt, new_pos = self.parse_statement(interpreter.tokens, interpreter.pos)
                    if stmt:
                        body.append(stmt)
                        interpreter.pos = new_pos
                    else:
                        # Move to next token if not parseable
                        consume()
                if peek() and peek()[0] == 'RIGHT_BRACE':
                    consume()  # Consume '}'
                    return ('WHILE', condition, body), interpreter.pos
        
        # Enhanced if statement with {} blocks
        elif token[0] == 'IDENTIFIER' and token[1] == 'sif':
            consume()  # Consume 'sif'
            condition, _ = self.interpreter.parse_expression(interpreter.tokens, interpreter.pos)
            if condition and peek() and peek()[0] == 'LEFT_BRACE':
                consume()  # Consume '{'
                body = []
                # Parse body statements until '}' or 'sle'
                while peek() and not (peek()[0] == 'RIGHT_BRACE' or 
                                     (peek()[0] == 'IDENTIFIER' and peek()[1] == 'sle')):
                    stmt, new_pos = self.parse_statement(interpreter.tokens, interpreter.pos)
                    if stmt:
                        body.append(stmt)
                        interpreter.pos = new_pos
                    else:
                        # Move to next token if not parseable
                        consume()
                
                if peek() and peek()[0] == 'IDENTIFIER' and peek()[1] == 'sle':
                    consume()  # Consume 'sle'
                    if peek() and peek()[0] == 'LEFT_BRACE':
                        consume()  # Consume '{'
                        else_body = []
                        # Parse else body until '}'
                        while peek() and not (peek()[0] == 'RIGHT_BRACE'):
                            stmt, new_pos = self.parse_statement(interpreter.tokens, interpreter.pos)
                            if stmt:
                                else_body.append(stmt)
                                interpreter.pos = new_pos
                            else:
                                # Move to next token if not parseable
                                consume()
                        if peek() and peek()[0] == 'RIGHT_BRACE':
                            consume()  # Consume '}'
                            return ('IF_ELSE', condition, body, else_body), interpreter.pos
                elif peek() and peek()[0] == 'RIGHT_BRACE':
                    consume()  # Consume '}'
                    return ('IF', condition, body), interpreter.pos
        
        return None, pos
    
    def execute_statement(self, stmt):
        """Execute enhanced statements"""
        if stmt[0] == 'WHILE':
            while self.interpreter.evaluate_expression(stmt[1]):
                for body_stmt in stmt[2]:
                    self.execute_statement(body_stmt)
            return True
        elif stmt[0] == 'IF_ELSE':
            condition = self.interpreter.evaluate_expression(stmt[1])
            if condition:
                for body_stmt in stmt[2]:
                    self.execute_statement(body_stmt)
            else:
                for else_stmt in stmt[3]:
                    self.execute_statement(else_stmt)
            return True
        elif stmt[0] == 'IF':
            condition = self.interpreter.evaluate_expression(stmt[1])
            if condition:
                for body_stmt in stmt[2]:
                    self.execute_statement(body_stmt)
            return True
        return False
