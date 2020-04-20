import os
import sys

path = os.getcwd()

class functions:

    def __init__(self):
        pass
    
    def f(self,x):
        return x*x
    
    def Trap(self,a,b,n,h):
        
        integral = (self.f(a) + self.f(b))/2.0
        
        x = a 
        for i in range(1,int(n)):
            x = x + h
            integral = integral + self.f(x)
            
        return integral*h


if __name__ == '__main__':

    func = functions()

    a = 0.0
    b = 1.0
    n = int(sys.argv[1])
    dest = 0
    total = -1.0

    h = (b-a)/n #h is the same for all processes 

    integral = func.Trap(a,b,n,h)

    print(integral)

