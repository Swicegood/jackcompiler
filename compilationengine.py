import symboltable
import re

class CompilationEngine:

    def __init__(self,outfile, mytokeizer, vw):
        self.outfile = outfile  
        self.mytokenizer = mytokeizer
        self.vw = vw          
        self.label = 0    
        self.voidsubs = []
        self.subdec = {}
        self.void = False
        self.array = False
        self.varinfoprev = {}
        self.CompileClass()

    def eat(self, strings):
        curretToken = self.mytokenizer.token
        if (curretToken not in strings):
            print("Error: "+str(strings)+" expected")
        else:
            self.mytokenizer.advance()

    def writeln(self):
        tok = self.mytokenizer.token
        if tok == '/eof':
            pass
        if tok == '<':
            tok = '&lt;'
        if tok == '>':
            tok = '&gt;'
        if tok == '&':
            tok = '&amp;'
        if tok[0] == '"':
            tok = self.mytokenizer.stringVal()
        toktype = str(self.mytokenizer.tokenType()).lower()
        if toktype == 'string_const':
            toktype = 'stringConstant'
        if toktype == 'int_const':
            toktype = 'integerConstant'
        writeline  = '<'+toktype+'> '+tok+' </'+toktype+'>\n'
        self.outfile.write(writeline)

    def writeID(self, name, type, cat, st):
        kind = None
        i = None
        if cat == 'class' or cat == 'subroutine':
            writeline= name+' '
            if type:
                writeline += type+' '
            writeline += cat+'\n'
        else:            
            if cat == 'var':
                cat = 'local'            
            # i = st.IndexOf(name)
            # kind = st.IndexOf(name)
            # if i is None:     #not found in current scope
            #     i = self.sc.IndexOf(name)  # what is the index inthe class leve scope
            # if i is not None:
            #     kind = self.sc.KindOf(name)
            #     type = self.sc.TypeOf(name) 
            #     if not kind:
            #         kind = st.KindOf(name)
            #         type = st.TypeOf(name)     
            i = st.IndexOf(name)
            kind = st.KindOf(name)
            if type == None:
                type = st.TypeOf(name)
            if st == self.ss:
                if i == None:
                    i = self.sc.IndexOf(name)
                if kind == None:
                    kind = self.sc.KindOf(name)
                if type == None:
                    type = self.sc.TypeOf(name)
            if i is not None:
                writeline = name+' '+type+' '+kind+' '+str(i)+' used\n'
            else: 
                if cat == None:
                    writeline = name+' '+'class\n'                  
                else:
                    st.define(name, type, cat)
                    i = st.IndexOf(name)
                    kind = st.KindOf(name)
                    type = st.TypeOf(name)
                    writeline = name+' '+type+' '+kind+' '+str(i)+' define\n'
        self.outfile.write(writeline)
        return {'segment':kind,'i':i}

    def next_label(self):
        self.label += 1
        return 'L'+str(self.label)

    def CompileClass(self):
        t = {}
        self.sc = symboltable.SymbolTable()
        self.outfile.write('<class>\n')
        self.mytokenizer.advance()        
        self.writeln() #class
        self.eat('class')
        if self.mytokenizer.tokenType() != 'IDENTIFIER':
            print("Error: Identifier expected ")
        self.writeln() #class name
        t['name'] = self.mytokenizer.token        
        self.writeID(t['name'], None,  'class', self.sc) 
        self.mytokenizer.advance()
        self.writeln() # {
        self.eat('{')
        while self.mytokenizer.token != '}':
            if self.mytokenizer.token in ['static', 'field']:  
                self.CompileClassVarDec()    
            if self.mytokenizer.token in ['constructor', 'function', 'method']:                   
                self.CompileSubroutineDec(t['name'])          
        self.writeln() # }
        self.eat('}')
        self.outfile.write('</class>\n')

    def CompileClassVarDec(self):
        t = {}
        self.outfile.write('<classVarDec>\n')
        self.writeln() #kind
        t['kind'] = self.mytokenizer.token                
        self.eat(['static', 'field'])
        self.writeln() #type
        t['ttype'] = self.mytokenizer.token 
        self.mytokenizer.advance()
        self.writeln()  # varName
        t['name'] = self.mytokenizer.token
        self.writeID(t['name'], t['ttype'], t['kind'], self.sc) 
        self.mytokenizer.advance()
        while self.mytokenizer.token != ';':
            self.writeln()  # ,
            self.eat(',')
            self.writeln()  # varName
            t['name'] = self.mytokenizer.token
            self.writeID(t['name'], t['ttype'], t['kind'], self.sc) 
            self.mytokenizer.advance()
        self.writeln()  # ;
        self.outfile.write('</classVarDec>\n')
        self.eat(';')

    def CompileSubroutineDec(self, classname):
        t = {}
        self.void = False
        self.ss = symboltable.SymbolTable()
        self.outfile.write('<subroutineDec>\n')
        self.writeln()   #keyword
        t['subroutine'] = self.mytokenizer.token
        if self.mytokenizer.token == 'method':
                    self.writeID('this', classname, 'argument', self.ss)
        self.mytokenizer.advance()
        self.writeln()    # void or type
        if self.mytokenizer.token == 'void':
            self.eat('void')
            self.void = True
        else:
            self.mytokenizer.advance()
        self.writeln()  # subroutineName
        t['subname'] = self.mytokenizer.token
        self.writeID(self.mytokenizer.token, None,  'subroutine', self.ss) 
        self.mytokenizer.advance()
        self.writeln()  # (
        self.eat('(')
        self.compileParameterList()
        self.writeln() #)
        self.eat(')')
        t['classname'] = classname
        self.subdec = t
        if t['subroutine'] == 'constructor':
            self.vw.writeFunction(self.subdec['classname']+'.'+self.subdec['subname'], 0)
            self.vw.writePush('constant', self.sc.VarCount('field'))
            self.vw.writeCall('Memory.alloc', 1)
            self.vw.writePop('pointer', 0)         
        self.outfile.write('<subroutineBody>\n')
        self.compileSubroutineBody()        
        self.outfile.write('</subroutineDec>\n')
       
    def compileParameterList(self):
        t = {}   #token attribute list
        self.pn = 0
        self.outfile.write('<parameterList>\n')  
        if self.mytokenizer.token != ')':             
            self.writeln()      #type
            t['ttype'] = self.mytokenizer.token
            self.mytokenizer.advance()
            self.writeln()         #varName
            t['name'] = self.mytokenizer.token
            t['kind'] = 'argument'
            self.writeID(t['name'], t['ttype'], t['kind'], self.ss) 
            self.mytokenizer.advance()
            self.pn = 1
            while self.mytokenizer.token != ')':  
                self.writeln() # ,          
                self.eat(',')  
                self.writeln()  #type
                t['ttype'] = self.mytokenizer.token
                self.mytokenizer.advance()
                self.writeln()  # varName
                t['name'] = self.mytokenizer.token
                self.writeID(t['name'], t['ttype'], t['kind'], self.ss) 
                self.mytokenizer.advance()
                self.pn +=1    
        self.outfile.write('</parameterList>\n') 

    def compileSubroutineBody(self):
        self.writeln() # {
        self.eat('{')
        while self.mytokenizer.token not in ['let', 'if', 'while', 'do', 'return']:
            if self.mytokenizer.token == 'var':
                self.compileVarDec()
            if self.mytokenizer.token == '}':
                self.writeln()  # }
                self.eat('}')
                return 
        if self.subdec['subroutine'] == 'function':
            self.vw.writeFunction(self.subdec['classname']+'.'+self.subdec['subname'], self.pn)
        if self.subdec['subroutine'] == 'method':
            self.vw.writeFunction(self.subdec['classname']+'.'+self.subdec['subname'], self.ss.VarCount('local'))
            self.vw.writePush('argument', 0)
            self.vw.writePop('pointer', 0)  
        self.compileStatements()
        self.outfile.write('</subroutineBody>\n')

    def compileVarDec(self):
        t = {}
        self.outfile.write('<varDec>\n')
        self.writeln()  #var
        self.eat('var')
        self.writeln()  #type
        t['ttype'] = self.mytokenizer.token
        self.mytokenizer.advance()
        self.writeln()  #varName
        t['name'] = self.mytokenizer.token
        self.writeID(t['name'], t['ttype'], 'local', self.ss)
        self.pn += 1
        self.mytokenizer.advance()
        while self.mytokenizer.token != ';':
            self.writeln()  # ,
            self.eat(',')
            self.writeln()  # varName
            t['name'] = self.mytokenizer.token
            self.writeID(t['name'], t['ttype'], 'var', self.ss)
            self.pn +=1
            self.mytokenizer.advance()
        self.writeln()  # ;
        self.outfile.write('</varDec>\n')
        self.eat(';')

    def compileStatements(self):        
        self.outfile.write('<statements>\n')  
        while self.mytokenizer.token != '}':
            if self.mytokenizer.token == 'let':
                self.compileLet()
            if self.mytokenizer.token == 'if':
                self.compileIf()
            if self.mytokenizer.token == 'while':
                self.compileWhile()
            if self.mytokenizer.token == 'do':
                self.compileDo()
            if self.mytokenizer.token == 'return':
                self.compileReturn()
        self.outfile.write('</statements>\n')
        self.writeln()  # }
        self.eat('}')


    def compileLet(self):
        array = False
        self.outfile.write('<letStatement>\n')
        self.writeln() # let
        self.mytokenizer.advance()
        self.writeln() #Identifier
        var = self.mytokenizer.token
        varinfo = self.writeID(self.mytokenizer.token, None, 'var', self.ss)
        self.mytokenizer.advance()
        if self.mytokenizer.token == '[':
            self.writeln()  # [
            self.eat('[')
            self.vw.writePush(varinfo['segment'], varinfo['i'])
            self.CompileExpression()
            self.vw.WriteArithmetic('add')
            self.writeln()  # ]
            self.eat(']')
            array = True
        self.writeln() # =
        self.eat('=')
        self.CompileExpression()
        self.writeln()  # ;
        self.eat(';')
        if array:
            self.vw.writePop('temp', 0)
            self.vw.writePop('pointer', 1)
            self.vw.writePush('temp', 0)
            self.vw.writePop('that', 0)
        else:
            if self.ss.KindOf(var) == None or self.ss.IndexOf(var) == None:
                if self.sc.KindOf(var) == 'field':
                    self.vw.writePop('this', self.sc.IndexOf(var))
                else:    # must be static
                    self.vw.writePop(self.sc.KindOf(var), self.sc.IndexOf(var))
            else:
                self.vw.writePop(self.ss.KindOf(var), self.ss.IndexOf(var))
        self.outfile.write('</letStatement>\n')

    def compileIf(self):
        self.outfile.write('<ifStatement>\n')
        self.writeln()  # if
        self.mytokenizer.advance()
        self.writeln() # (
        self.eat('(')
        self.CompileExpression()
        self.writeln() # )
        self.eat(')')
        self.vw.WriteArithmetic('not')
        l1 = self.next_label()
        self.vw.WriteIf(l1)
        self.writeln() # {
        self.eat('{')
        self.compileStatements()
        l2 = self.next_label()
        self.vw.WriteGoto(l2)
        self.vw.WriteLabel(l1)
        if self.mytokenizer.token == 'else':
            self.writeln()  # else 
            self.mytokenizer.advance()
            self.writeln()  # {
            self.eat('{')
            self.compileStatements()
        self.vw.WriteLabel(l2)
        self.outfile.write('</ifStatement>\n')

    def compileWhile(self):
        self.outfile.write('<whileStatement>\n')
        self.writeln()  # while
        l1 = self.next_label()
        self.vw.WriteLabel(l1)
        self.mytokenizer.advance()
        self.writeln()  # (
        self.eat('(')
        self.CompileExpression()
        self.writeln()  # )
        self.eat(')')
        self.vw.WriteArithmetic('not')
        l2 = self.next_label()
        self.vw.WriteIf(l2)
        self.writeln() # {
        self.eat('{')
        self.compileStatements()
        self.vw.WriteGoto(l1)
        self.vw.WriteLabel(l2)
        self.outfile.write('</whileStatement>\n')

    def compileDo(self):
        t = {}
        obj = 0
        self.outfile.write('<doStatement>\n')
        self.writeln()  # do
        self.mytokenizer.advance()
        self.writeln()  #Identifier
        t['class'] = self.mytokenizer.token
        self.writeID(self.mytokenizer.token,  None, 'subroutine', self.ss)
        self.mytokenizer.advance()
        t['subroutine'] = ''
        if self.mytokenizer.token == '.':
            self.writeln() # .
            self.eat('.')
            self.writeln() # subroutineName
            self.writeID(self.mytokenizer.token,  None, 'subroutine', self.ss)
            t['subroutine'] = self.mytokenizer.token
            self.mytokenizer.advance()
        if t['subroutine'] == '':
            t['subroutine'] = t['class']
            t['class'] = self.subdec['classname']
            self.vw.writePush('pointer', 0)
            obj = 1
        varname = t['class']
        if self.ss.KindOf(varname) == 'local':
            t['class'] = self.ss.TypeOf(varname)
            self.vw.writePush(self.ss.KindOf(varname), self.ss.IndexOf(varname))
            obj = 1
        elif self.sc.KindOf(varname) == 'field':
            t['class'] = self.sc.TypeOf(varname)
            self.vw.writePush('this', self.sc.IndexOf(varname))
            obj = 1
        self.writeln() # (
        self.eat('(')
        self.CompileExpressionList()
        self.writeln()  # (
        self.eat(')')
        self.writeln()  # ;
        self.eat(';')
        self.vw.writeCall(t['class']+'.'+t['subroutine'], self.en + obj)        
        self.vw.writePop('temp', 0)
        self.outfile.write('</doStatement>\n')

    def compileReturn(self):
        self.outfile.write('<returnStatement>\n')
        self.writeln()  # return
        self.mytokenizer.advance()
        if self.mytokenizer.token != ';':
            self.CompileExpression()
        self.writeln()  # ;
        self.eat(';')        
        if self.void:
            self.vw.writePush('constant', 0)
        self.vw.writeReturn()
        self.outfile.write('</returnStatement>\n')
    
    def CompileExpression(self):
        self.outfile.write('<expression>\n')
        self.ComplileTerm()
        while self.mytokenizer.token in ['+','-','*','/','&','|','<','>','=']:
            self.writeln() # op
            op = self.mytokenizer.token           
            self.mytokenizer.advance()
            self.ComplileTerm()
            if op == '+':
                self.vw.WriteArithmetic('add')
            if op == '-':
                self.vw.WriteArithmetic('sub')
            if op == '*':
                self.vw.writeCall('Math.multiply', 2)
            if op == '/':
                self.vw.writeCall('Math.divide', 2)
            if op == '&':
                self.vw.WriteArithmetic('and')
            if op == '|':
                self.vw.WriteArithmetic('or')
            if op == '=':
                self.vw.WriteArithmetic('eq')
            if op == '>':
                self.vw.WriteArithmetic('gt')
            if op == '<':
                self.vw.WriteArithmetic('lt')
        self.outfile.write('</expression>\n')

    def ComplileTerm(self):
        t = {}
        varinfo = {}
        varname = None
        self.outfile.write('<term>\n')
        if self.mytokenizer.tokenType() == 'IDENTIFIER':
            varname = self.mytokenizer.token
            self.mytokenizer.advance()
            if self.mytokenizer.token == '[':
                self.outfile.write('<identifier> '+varname+' </identifier>\n')
                varinfo = self.writeID(varname, None, 'var', self.ss)
                if varinfo['segment'] == 'field':
                    varinfo['segment'] = 'this'
                if varinfo:
                    self.vw.writePush(varinfo['segment'], varinfo['i'])
                self.array = True
                self.writeln() # [
                self.eat('[')
                self.CompileExpression()
                self.writeln() # ]
                self.eat(']') 
                self.vw.WriteArithmetic('add')
                self.vw.writePop('pointer', 1)
                self.vw.writePush('that', 0)
                # if varinfo and not self.array:
                #     self.vw.writePush(varinfo['segment'], varinfo['i'])       
                self.array = False
            else:
                #general identifier
                self.outfile.write('<identifier> '+varname+' </identifier>\n')
                varinfo = self.writeID(varname, None, None, self.ss)
                if self.mytokenizer.token == '(':
                    self.writeln()  # (
                    self.eat('(')
                    self.CompileExpressionList()
                    self.writeln() # )
                    self.eat(')')
                elif self.mytokenizer.token == '.':
                    self.writeln()  # .
                    self.eat('.')
                    self.writeln()  # subroutine name
                    sub = self.mytokenizer.token
                    self.writeID(self.mytokenizer.token, None, 'subroutine', self.ss)
                    self.mytokenizer.advance()
                    self.writeln()  # (
                    self.eat('(')
                    self.CompileExpressionList()
                    self.writeln()  # )
                    self.eat(')')
                    if self.ss.TypeOf(varname):
                        if re.match(r'^[A-Z]', self.ss.TypeOf(varname)):
                            self.vw.writePush('this', self.ss.IndexOf(varname))
                            self.vw.writeCall(self.ss.TypeOf(varname)+'.'+sub, self.en+1)
                    elif self.sc.TypeOf(varname):
                        if re.match(r'^[A-Z]', self.sc.TypeOf(varname)):
                            self.vw.writePush('this', self.sc.IndexOf(varname))
                            self.vw.writeCall(self.sc.TypeOf(varname)+'.'+sub, self.en+1)
                    else:
                        self.vw.writeCall(varname+'.'+sub, self.en)
                else:
                    if self.ss.IndexOf(varname):
                        varinfo['segment'] = self.ss.KindOf(varname)
                        varinfo['i'] =  self.ss.IndexOf(varname)
                    elif self.sc.IndexOf(varname): 
                        varinfo['segment'] = self.sc.KindOf(varname)
                        varinfo['i'] =  self.sc.IndexOf(varname)
                    if varinfo['segment'] == 'field':
                        varinfo['segment'] = 'this'
                    self.vw.writePush(varinfo['segment'], varinfo['i'])
        elif self.mytokenizer.token == '(':
                 self.writeln() # (
                 self.eat('(')
                 self.CompileExpression()
                 self.writeln()  # )
                 self.eat(')')
        elif self.mytokenizer.token == '~' or self.mytokenizer.token == '-':
            self.writeln() # Unary op
            unop = self.mytokenizer.token
            self.mytokenizer.advance()
            self.ComplileTerm()
            if unop == '-':
                self.vw.WriteArithmetic('neg')
            if unop == '~':
                self.vw.WriteArithmetic('not')           
        elif self.mytokenizer.token == 'this':
                self.vw.writePush('pointer',0)
                self.mytokenizer.advance()
        elif self.mytokenizer.token == "true":
                self.vw.writePush('constant', 1)
                self.vw.WriteArithmetic('neg')
                self.mytokenizer.advance()
        elif self.mytokenizer.token == "false":
            self.vw.writePush('constant', 0)
            self.mytokenizer.advance()
        elif self.mytokenizer.token == 'null':
            self.vw.writePush('constant', 0)
            self.mytokenizer.advance()
        elif self.mytokenizer.tokenType() == 'INT_CONST': 
            self.vw.writePush('constant', self.mytokenizer.token)
            self.mytokenizer.advance()
        elif self.mytokenizer.tokenType() == 'STRING_CONST':
            self.vw.writePush('constant', len(self.mytokenizer.token)-2)
            self.vw.writeCall('String.new', 1)
            for char in self.mytokenizer.token[1:-1]:
                self.vw.writePush('constant', ord(char))
                self.vw.writeCall('String.appendChar', 2)
            self.mytokenizer.advance()
        self.outfile.write('</term>\n')

    def CompileExpressionList(self):
        self.outfile.write('<expressionList>\n')
        self.en = 0   #number of expressions in list
        while self.mytokenizer.token != ')':            
            self.CompileExpression()
            self.en += 1
            if self.mytokenizer.token == ',':
                self.writeln()  # ,
                self.eat(',')            
        self.outfile.write('</expressionList>\n')
        