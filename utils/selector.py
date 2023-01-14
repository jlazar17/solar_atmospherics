def make_conj(f1,f2):
    def conj(frame):
        c1=f1(frame)
        if(not c1):
            return(False)
        return(f2(frame))
    return(conj)
def make_disj(f1,f2):
    def disj(frame):
        c1=f1(frame)
        if(c1):
            return(True)
        return(f2(frame))
    return(disj)

class selector(object):
    def __init__(self,func):
        self.func=func
    def __call__(self,frame):
        return(self.func(frame))
    def __and__(self,other):
        return(selector(make_conj(self.func,other.func)))
    def __or__(self,other):
        return(selector(make_disj(self.func,other.func)))
    def __invert__(self):
        return(selector(lambda frame: not self.func(frame)))
