import os, hashlib
import dill
class Persister:
    def __init__(self, grader, sessionId = "default", restart = False, forcedStart = False):
        self.session = sessionId
        self.grader = grader
        self.workSpacePath = "/tmp/csAg/"
        self.sessionPath = os.path.join(self.workSpacePath,sessionId)
        self.lockPath = os.path.join(self.workSpacePath,".lock")
        self.hash = hashlib.md5(self.grader.extractor.destDir.encode()).hexdigest()
        self.picklePath = os.path.join(self.sessionPath,f".p_{self.hash}")
        self.forcedStart = forcedStart
        self.restart = restart
        os.makedirs(self.workSpacePath, exist_ok=True)
        os.makedirs(self.sessionPath, exist_ok=True)

    def __enter__(self):
        with open(self.lockPath,"w+") as lock:
            if self.hash in lock.readlines(): 
                assert self.forcedStart, "can't run multiple grader on same srcDir"
            else: lock.writelines([self.hash])
        if os.path.isfile(self.picklePath) and self.restart==False: 
            with open(self.picklePath,"rb") as pickleFile:
                self.grader = dill.load(pickleFile)
        return self.grader
        
    

    def __exit__(self, _, __, ___):
        with open(self.lockPath,"r+") as f:
            new_f = f.readlines()
            f.seek(0)
            for line in new_f:
                if self.hash not in line:
                    f.write(line)
            f.truncate()
        with open(self.picklePath,"wb") as pickleFile:
            dill.dump(self.grader,pickleFile)
        
