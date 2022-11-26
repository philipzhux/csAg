import os, parse, glob
import pandas as pd
import subprocess
class Mosser:
    def __init__(self, srcDir, language, extension, studentList, templateFile = None):
        self.srcDir = srcDir
        self.language = language
        self.extension = extension
        self.templateFile = os.path.abspath(templateFile)
        self.studentList = studentList
        self.mossPath = os.path.join(os.path.dirname(__file__), 'moss.pl')
        self.url = None
        self.results = []
    
    def setResultUrl(self,url):
        self.url = url
    
    def runMoss(self):
        if self.templateFile: templateFile = f"-b {self.templateFile}"
        else: templateFile = ""
        srcPath = os.path.join(self.srcDir,f"*.{self.extension}")
        srcPath = " ".join(glob.glob(srcPath))
        commands = f"-l {self.language} {templateFile} {srcPath}"
        print(["/usr/bin/perl", self.mossPath]+commands.split())
        p = subprocess.run(["/usr/bin/perl", self.mossPath]+commands.split(), capture_output=True, text=True)
        print(p.stderr)
        print(p.stdout)
        out = p.stdout
        if(out): self.url = out.split()[0]
    
    def parseMoss(self):
        rec = dict()
        table_results = pd.read_html(self.url.split()[0])
        for _ ,row in table_results[0].iterrows():
            parse_res = parse.parse("{}/{}."+self.extension+" ({}%)",row[0])
            n1,p1 = parse_res[1], int(parse_res[2])
            n1 = n1.split("/")[-1]
            parse_res = parse.parse("{}/{}."+self.extension+" ({}%)",row[1])
            n2,p2 = parse_res[1], int(parse_res[2])
            n2 = n2.split("/")[-1]
            sim = max(p1,p2)
            if not n1 in rec: rec[n1] = [sim,[n2]]
            else: 
                rec[n1][0] = max(sim,rec[n1][0])
                rec[n1][1].append(n2)
            if not n2 in rec: rec[n2] = [sim,[n1]]
            else: 
                rec[n2][0] = max(sim,rec[n2][0])
                rec[n2][1].append(n1)
        st = sorted(rec.items(),key = lambda x: x[1][0],reverse=True)
        for ste in st:
            if ste[0] in self.studentList: self.results.append(ste)
        
    
    def printRes(self):
        for r in self.results:
            print(f"{r[0]}\t{r[1][0]}\t{r[1][1]}")
    
    def getSuspectedStudents(self,threshold = 40):
        sus = []
        for r in self.results:
            if r[1][0]>threshold: sus.append(r[0])
        print("Problemetic Student list:",sus)
        print("Email addresses list, copyable to Outlook client:")
        for s in sus:
            print(f"{s}@link.cuhk.edu.cn;")
        
        
