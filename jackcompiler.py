import jack_tokenizer
import compilationengine
import sys
from os import path, listdir
import vmwriter

if len(sys.argv) > 1:
    dir = sys.argv[1]
else:
    dir = "../../nand2tetris/projects/11/ComplexArrays/"
for fname in listdir(dir):
    if fname.split(".")[1] == 'jack':
        pathname = path.join(dir,fname)
        mytokenizer = jack_tokenizer.JackTokenizer(pathname)
        of = open(fname+".xml", "w")
        vw = vmwriter.VMWriter(fname)
        mycomilationengine = compilationengine.CompilationEngine(of, mytokenizer, vw)
        of.close()