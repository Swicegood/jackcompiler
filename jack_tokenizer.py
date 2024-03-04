import re

keywords = ['class',
            'constructor',
            'function',
            'method',
            'field',
            'static',
            'var',
            'int',
            'char',
            'boolean',
            'void',
            'true',
            'false',
            'null',
            'this',
            'let',
            'do',
            'if',
            'else',
            'while',
            'return'
            ]

symbols = ['{',
           '}',
           '(',
           ')',
           '[',
           ']',
           '.',
           ',',
           ';',
           '+',
           '-',
           '*',
           '/',
           '&',
           '|',
           '<',
           '>',
           '=',
           '~'
          ]

class JackTokenizer:

    def __init__(self, file):
        f = open(file,"r")
        self.input = f.readlines()
        self.i = 0
        self.j = 0
        self.line = self.input[self.i]
        self.token = ''
        pass

    def hasMoreTokens(self):  
        if (self.i < len(self.input)-1):
            return True
        if (self.i == len(self.input)):
            if (len(self.input[self.i][self.j]) != '\n'):
                return True
        return False
    
    def advance(self):
        self.token = ''  
        # Skip all whitespace and comments      
        while True:
            line = self.input[self.i]
            while re.match('\s',line[self.j]):
                if line[self.j] == '\n':
                    self.i += 1
                    self.j = 0
                    if self.i < len(self.input):
                        line = self.input[self.i]
                    else:
                        self.token = '/eof'
                        return
                    continue
                self.j += 1
                
            if line[self.j] == '/':
                if line[self.j+1] == '/':
                    self.i += 1
                    self.j = 0
                elif line[self.j+1] == '*' and self.j < (len(line)-1):
                    if line[self.j+2] == '*':
                        self.j += 3
                        while True:
                            if line[self.j] == '\n':
                                self.i += 1
                                self.j = 0
                                line = self.input[self.i]
                                continue
                            if  self.j < (len(line)-2) and line[self.j] == '*' and  line[self.j+1] == '/':
                                self.i += 1
                                self.j = 0
                                line = self.input[self.i]
                                break                           
                            self.j += 1
                else:
                    break
            else:
                break

        # Handle the case of digits        
        if re.match('^\d+$',line[self.j]):
            while re.match('^\d+$',line[self.j]):
                self.token += line[self.j]
                self.j += 1
            return
        # Symboys are easy
        if line[self.j] in symbols:
            self.token = line[self.j]
            self.j += 1
            return

        #Indetifiers
        if re.match('^[a-zA-Z]',line[self.j]):
            while re.match('\w',line[self.j]):
                self.token += line[self.j]
                self.j += 1
            return

        #String literals
        if line[self.j] == '"':
            while True:
                self.token += line[self.j]
                self.j += 1
                if line[self.j] == '"':
                    self.token += line[self.j]
                    self.j += 1
                    break
            return

    def tokenType(self):
        if self.token in keywords:
            return "KEYWORD"
        elif self.token in symbols:
            return "SYMBOL"
        elif re.match('^[a-zA-Z]',self.token):
            return "IDENTIFIER"
        elif re.match('^\d+$',self.token):
            return "INT_CONST"
        elif self.token[0] == '"':
            return "STRING_CONST"

    def keyWord(self):
        for k in keywords:
            if self.token == k:                
                return k.upper()

    def symbol(self):
        return self.token

    def indentifier(self):
        return self.token
    
    def intVal(self):
        return int(self.token)

    def stringVal(self):
        return self.token.strip('"')
        