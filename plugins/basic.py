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
        # 不修改全局状态，使用局部变量
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
                        expr, new_pos = self.interpreter.parse_expression(tokens, local_pos)
                        if expr:
                            local_pos = new_pos
                            return ('ASSIGN', var_name, expr), local_pos
        elif token[0] == 'IDENTIFIER' and token[1] == 'sout':
            # Print statement: sout : "Hello World!"
            consume()  # Consume 'sout'
            if peek() and peek()[0] == 'ASSIGN':
                # Handle sout : "Hello World!"
                consume()  # Consume ':'
                # 直接获取下一个令牌作为表达式，绕过 parse_expression
                if local_pos < len(tokens):
                    expr = tokens[local_pos]
                    local_pos += 1
                    return ('PRINT', expr), local_pos
        elif token[0] == 'IDENTIFIER' and token[1] == 'sif':
            # If statement: sif condition | ...
            consume()  # Consume 'sif'
            condition, new_pos = self.interpreter.parse_expression(tokens, local_pos)
            if condition and new_pos < len(tokens) and tokens[new_pos][0] == 'SEPARATOR':
                consume()  # Consume '|'
                body = []
                # Parse body statements
                while peek() and not (peek()[0] == 'IDENTIFIER' and peek()[1] in ['selif', 'sle']):
                    stmt, new_pos = self.parse_statement(tokens, local_pos)
                    if stmt:
                        body.append(stmt)
                        local_pos = new_pos
                return ('IF', condition, body), local_pos
        elif token[0] == 'IDENTIFIER' and token[1] == 'sde':
            # Function definition or call: sde add : ... end or sde run<add>
         
            consume()  # Consume 'sde'
            
            # Check for function call: sde run<add>
            next_token = peek()

            if next_token and next_token[0] == 'IDENTIFIER' and next_token[1] == 'run':

                consume()  # Consume 'run'
                # Check for <function_name>

                if peek() and peek()[0] == 'OPERATOR' and peek()[1] == '<':

                    consume()  # Consume '<'
                    func_token = peek()

                    if func_token and func_token[0] == 'IDENTIFIER':
                        func_name = func_token[1]

                        consume()  # Consume function name

                        if peek() and peek()[0] == 'OPERATOR' and peek()[1] == '>':

                            consume()  # Consume '>'

                            return ('FUNCTION_CALL', func_name), local_pos

            
            # Check for function definition: sde add :
            func_token = peek()
            if not func_token or func_token[0] != 'IDENTIFIER':
                return None, pos
            func_name = func_token[1]
            consume()  # Consume function name
            
            # Check for assignment operator
            assign_token = peek()
            if not assign_token or assign_token[0] != 'ASSIGN':
                return None, pos
            consume()  # Consume ':'
            
            # Get function body until 'end'
            body_tokens = []
            while local_pos < len(tokens):
                current_token = tokens[local_pos]
                if current_token[0] == 'IDENTIFIER' and current_token[1] == 'end':
                    break
                body_tokens.append(current_token)
                local_pos += 1
            
            # Check for 'end'
            if local_pos < len(tokens) and tokens[local_pos][0] == 'IDENTIFIER' and tokens[local_pos][1] == 'end':
                consume()  # Consume 'end'
                return ('FUNCTION_DEF', func_name, body_tokens), local_pos
            return None, pos
        elif token[0] == 'IDENTIFIER' and peek(1) and peek(1)[0] == 'ASSIGN':
            # Direct assignment: a : 1
            # Check if this is not a time statement (let time plugin handle it)
            # Also check if this is not a sif or swhile statement (let siew plugin handle it)
            # Also check if this is not a suibtn statement (let sbtn plugin handle it)
            # Also check if this is not a web_get, web_post, web_put or web_delete statement (let web plugin handle it)
            # Also check if this is not a qr_text, qr_ascii or qr_png statement (let qrcode plugin handle it)
            # Also check if this is not a progress, spinner or loading_bar statement (let progress plugin handle it)
            # Also check if this is not a dice, coin, rps or guess_num statement (let game plugin handle it)
            # Also check if this is not a file_write, file_read, file_append, file_delete or dir_list statement (let fileio plugin handle it)
            if token[1] != 'time' and token[1] not in ['sif', 'swhile', 'suibtn', 'sysinfo', 'md5', 'sha256', 'base64_enc', 'base64_dec', 'rot13', 'list_create', 'list_add', 'list_show', 'list_len', 'list_get', 'list_remove', 'map_create', 'map_set', 'map_get', 'map_has', 'map_keys', 'map_values', 'map_clear', 'richtext', 'style', 'rainbow_text', 'typewriter', 'marquee', 'clear_text', 'color_block', 'qr_text', 'qr_ascii', 'qr_png', 'progress', 'spinner', 'loading_bar', 'dice', 'coin', 'rps', 'guess_num', 'file_write', 'file_read', 'file_append', 'file_delete', 'dir_list']:
                var_name = consume()[1]
                consume()  # Consume ':'
                
                # Check if this is a web_get, web_post, web_put or web_delete statement
                if local_pos < len(tokens) and tokens[local_pos][0] == 'IDENTIFIER' and tokens[local_pos][1] in ['web_get', 'web_post', 'web_put', 'web_delete']:
                    # Return None to let web plugin handle it
                    return None, pos
                
                # Check if this is a color or rainbow statement (let color plugin handle it)
                if var_name in ['color', 'rainbow']:
                    # Return None to let color plugin handle it
                    return None, pos
                
                # Check if this is a scui statement (let scui plugin handle it)
                if var_name == 'scui':
                    # Return None to let scui plugin handle it
                    return None, pos
                
                # Check if this is a richtext statement (let richtext plugin handle it)
                if var_name in ['richtext', 'style', 'rainbow_text', 'typewriter', 'marquee', 'clear_text', 'color_block']:
                    # Return None to let richtext plugin handle it
                    return None, pos
                
                expr, new_pos = self.interpreter.parse_expression(tokens, local_pos)
                if expr:
                    local_pos = new_pos
                    return ('ASSIGN', var_name, expr), local_pos
        
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
        elif stmt[0] == 'FUNCTION_DEF':
            # Function definition: store function in variables
            func_name = stmt[1]
            func_body = stmt[2]  # This is a list of tokens
            # Store function body as a list of tokens
            self.interpreter.variables[func_name] = func_body
            if hasattr(self.interpreter, 'debug_mode') and self.interpreter.debug_mode:
                print(f"Debug: Defined function '{func_name}' with body tokens: {func_body}")
            return True
        elif stmt[0] == 'FUNCTION_CALL':
            # Function call: execute stored function body
            func_name = stmt[1]
            if func_name in self.interpreter.variables:
                func_body = self.interpreter.variables[func_name]
                if hasattr(self.interpreter, 'debug_mode') and self.interpreter.debug_mode:
                    print(f"Debug: Calling function '{func_name}'")
                # Execute each statement in the function body
                # We need to parse and execute the tokens
                pos = 0
                while pos < len(func_body):
                    # Parse statement from the function body tokens
                    stmt, new_pos = self.parse_statement(func_body, pos)
                    if stmt:
                        self.execute_statement(stmt)
                        pos = new_pos
                    else:
                        pos += 1
                return True
            else:
                if hasattr(self.interpreter, 'debug_mode') and self.interpreter.debug_mode:
                    print(f"Debug: Function '{func_name}' not found")
                return False
        return False
