class VMWriter:

    def __init__(self, fname) -> None:
        self.of = open(fname.split('.')[0]+".vm", "w")

    def writePush(self, segment, index):
        writeline = 'push '+segment+' '+str(index)+'\n'
        self.of.write(writeline)

    def writePop(self, segment, index):
        writeline = 'pop '+segment+' '+str(index)+'\n'
        self.of.write(writeline)

    def WriteArithmetic(self, command):
        self.of.write(command+'\n')

    def WriteLabel(self, label):
        self.of.write('label '+label+'\n')

    def WriteGoto(self, label):
        self.of.write('goto '+label+'\n')

    def WriteIf(self, label):
        self.of.write('if-goto '+label+'\n')

    def writeCall(self, name, nArgs):
        self.of.write('call '+name+' '+str(nArgs)+'\n')

    def writeFunction(self, name, nLocals):
        self.of.write('function '+name+' '+str(nLocals)+'\n')

    def writeReturn(self):
        self.of.write('return\n')
        
    def close(self):
        self.of.close()