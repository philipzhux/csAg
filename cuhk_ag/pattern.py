from parse import parse
from time import time

class Pattern:
    def __init__(self,format = ("{}_{}_{}",1)):
        def parser(s):
            try:
                ret = parse(format[0],s)[format[1]]
            except:
                ret = f"unknown_{time()}"
            return ret
        self.parser = parser

    def parse(self,s):
        return self.parser(s)
    

if __name__=="__main__":
    p = Pattern()
    print(p.parser("Assignment 2_117010167_attempt_2022-10-24-18-34-32_Assignment_2_117010167"))

