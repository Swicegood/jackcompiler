import jack_tokenizer
import sys
from os import path, listdir

#dir = sys.argv[1]
dir = "../../nand2tetris/projects/10/ExpressionLessSquare"
for fname in listdir(dir):
    if fname.split(".")[1] == 'jack':
        pathname = path.join(dir,fname)
        mytokenizer = jack_tokenizer.JackTokenizer(pathname)
        of = open(fname+".xml", "w")
        of.write('<tokens>\n')
        while mytokenizer.hasMoreTokens():
            mytokenizer.advance()
            tok = mytokenizer.token
            if tok == '/eof':
                break
            if tok == '<':
                tok = '&lt;'
            if tok == '>':
                tok = '&gt;'
            if tok == '&':
                tok = '&amp;'
            if tok[0] == '"':
                tok = mytokenizer.stringVal()
            toktype = str(mytokenizer.tokenType()).lower()
            if toktype == 'string_const':
                toktype = 'stringConstant'
            if toktype == 'int_const':
                toktype = 'integerConstant'

            writeline  = '<'+toktype+'> '+tok+' </'+toktype+'>\n'
            of.write(writeline)
        of.write('</tokens>\n')
        of.close()