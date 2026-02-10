# Basic syntax plugin for SunsetCodeLang

class BasicPlugin:
    def __init__(self, interpreter):
        self.interpreter = interpreter
    
    def register_syntax(self):
        """Register basic syntax handlers"""
        # This will be called by the interpreter to register syntax handlers
        pass
    
    def parse_statement(self, tokens, pos):
        """Parse basic statements"""
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
        
        if token[0] == 'IDENTIFIER' and token[1] == 'set':
            # Variable declaration: set a | a : 1
            consume()  # Consume 'set'
            var_name = consume()[1]  # Get variable name
            if peek() and peek()[0] == 'SEPARATOR':
                consume()  # Consume '|'
                # Check if next is the same variable for assignment
                if peek() and peek()[0] == 'IDENTIFIER' and peek()[1] == var_name:
                    consume()  # Consume variable name
                    if peek() and peek()[0] == 'ASSIGN':
                        consume()  # Consume ':'
                        expr, _ = self.interpreter.parse_expression(interpreter.tokens, interpreter.pos)
                        if expr:
                            interpreter.pos = self.interpreter.pos
                            return ('ASSIGN', var_name, expr), interpreter.pos
        elif token[0] == 'IDENTIFIER' and token[1] == 'sout':
            # Print statement: sout : "Hello World!"
            consume()  # Consume 'sout'
            if peek() and peek()[0] == 'ASSIGN':
                consume()  # Consume ':'
                expr, _ = self.interpreter.parse_expression(interpreter.tokens, interpreter.pos)
                if expr:
                    interpreter.pos = self.interpreter.pos
                    return ('PRINT', expr), interpreter.pos
        elif token[0] == 'IDENTIFIER' and token[1] == 'sif':
            # If statement: sif condition | ...
            consume()  # Consume 'sif'
            condition, _ = self.interpreter.parse_expression(interpreter.tokens, interpreter.pos)
            if condition and peek() and peek()[0] == 'SEPARATOR':
                consume()  # Consume '|'
                body = []
                # Parse body statements
                while peek() and not (peek()[0] == 'IDENTIFIER' and peek()[1] in ['selif', 'sle']):
                    stmt, new_pos = self.parse_statement(interpreter.tokens, interpreter.pos)
                    if stmt:
                        body.append(stmt)
                        interpreter.pos = new_pos
                return ('IF', condition, body), interpreter.pos
        elif token[0] == 'IDENTIFIER' and peek(1) and peek(1)[0] == 'ASSIGN':
                # Direct assignment: a : 1
                # Check if this is not a time statement (let time plugin handle it)
                if token[1] != 'time':
                    var_name = consume()[1]
                    consume()  # Consume ':'
                    expr, _ = self.interpreter.parse_expression(interpreter.tokens, interpreter.pos)
                    if expr:
                        interpreter.pos = self.interpreter.pos
                        return ('ASSIGN', var_name, expr), interpreter.pos
        
        return None, pos
    
    def execute_statement(self, stmt):
        """Execute basic statements"""
        if stmt[0] == 'ASSIGN':
            var_name = stmt[1]
            value = self.interpreter.evaluate_expression(stmt[2])
            self.interpreter.variables[var_name] = value
            return True
        elif stmt[0] == 'PRINT':
            value = self.interpreter.evaluate_expression(stmt[1])
            print(value)
            return True
        elif stmt[0] == 'IF':
            condition = self.interpreter.evaluate_expression(stmt[1])
            if condition:
                for body_stmt in stmt[2]:
                    self.execute_statement(body_stmt)
            return True
        return False
