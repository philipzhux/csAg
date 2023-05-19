from parse import parse
from time import time

class Pattern:
    def __init__(self,format = ("{}_{}_{}",1)):
        self.format = format
    
    def parse(self,s):
        try:
            ret = parse(self.format[0],s)[self.format[1]]
        except:
            ret = f"unknown_{time()}"
        return ret
    

if __name__=="__main__":
    p = Pattern()
    print(p.parser("Assignment 2_117010167_attempt_2022-10-24-18-34-32_Assignment_2_117010167"))

