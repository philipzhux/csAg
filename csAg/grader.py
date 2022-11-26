from .pattern import Pattern
from .extract import Extracter
import os, subprocess, tempfile, json, shlex
class Grader:
    def __init__(self, concernFiles, compiling, running, grading, scoreJSON, extractor):
        self.compiled_output = dict()
        self.run_output = dict()
        self.scores = dict()
        self.compiling = compiling
        self.running = running
        self.grading = grading
        self.concernFiles = concernFiles
        self.scoreJSON = scoreJSON
        self.extractor = extractor

    def compileAll(self):
        if not self.extractor.extracted: self.extractor.extract()
        for sid in self.extractor.getStudentList():
            workspacePath = self.extractor.getCodeDirPath(sid)
            if workspacePath: self.compiled_output[sid] = self.compiling(workspacePath)
    
            
    def runAll(self, each_timeout = 10):
        for sid in self.compiled_output:
            runCommand = self.running(self.compiled_output[sid])
            outputFile = os.path.join(tempfile.gettempdir(),f"{sid}.output")
            self.run_output[sid] = outputFile
            if "|" in runCommand:    
                cmd_parts = runCommand.split('|')
            else:
                cmd_parts = []
                cmd_parts.append(runCommand)
            i = 0
            p = {}
            with open(outputFile,"w") as output:
                for cmd_part in cmd_parts:
                    cmd_part = cmd_part.strip()
                    if i == 0:
                        p[i]=subprocess.Popen(shlex.split(cmd_part),stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    elif i == len(cmd_parts)-1:
                        p[i]=subprocess.Popen(shlex.split(cmd_part),stdin=p[i-1].stdout, stdout=output, stderr=output)
                    else:
                        p[i]=subprocess.Popen(shlex.split(cmd_part),stdin=p[i-1].stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    i = i +1
                exit_code = p[0].wait(each_timeout)
    
    def gradeAll(self, manual = False):
        for sid in self.run_output:
            if sid in self.scores: continue
            if not manual: self.scores[sid] = self.grading(self.run_output[sid])
            else:
                print(f"============== Manually scoring for {sid} ==============")
                print("Program Output:")
                with open(self.run_output[sid],"r") as outputFile:
                    for line in outputFile.getlines(): print(line)
                print(f"============== End of program output ==============")
                while True:
                    score = input("Input the student score, -1 to save parital results: ")
                    try: 
                        score = float(score)
                        if score==-1: self.saveScore(append=True)
                        else: break
                    except: 
                        print("Interrupted, saving partial results.")
                self.scores[sid] = score

    def saveScore(self, scoreJSON = None, append = False):
        if not scoreJSON: scoreJSON = self.scoreJSON
        with open(scoreJSON,"a+" if append else "w") as outFile:
            json.dump(self.scores,outFile)

    


        