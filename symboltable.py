class SymbolTable:

    def __init__(self) -> None:
        self.t = {}

    def define(self, name, type, kind):
        i = 0
        for value in self.t.values():
            if value[1] == kind:
                i += 1
        self.t[name] = [type, kind, i]
        pass

    def VarCount(self, kind):
        i = 0 
        for value in self.t.values():
            if value[1] == kind:
                i += 1
        return i

    def KindOf(self, name):
        for key in self.t.keys():
            if key == name:
                return self.t[key][1]
        return None

    def TypeOf(self, name):
        for key in self.t.keys():
            if key == name:
                return self.t[key][0]

    def IndexOf(self, name):
         for key in self.t.keys():
            if key == name:
                return self.t[key][2]

    