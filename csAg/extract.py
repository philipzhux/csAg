from .pattern import Pattern
import os, zipfile, glob
class Extracter:
    def __init__(self, featureFiles, srcDir , destDir, pattern = Pattern(), skipExtract = False):
        self.srcDir = srcDir
        self.destDir = destDir
        self.pattern = pattern
        self.studentList = []
        self.extracted = False
        self.featureFiles = featureFiles
        if skipExtract: self.skipExtract()
    
    def skipExtract(self):
        for ent in glob.glob(self.destDir):
            fn = ent.split("/")[-1]
            if fn.isnumeric(): 
                self.studentList.append(fn)
                self.extracted = True


    def extract(self):
        os.makedirs(self.destDir, exist_ok=True)
        for fn in os.listdir(self.srcDir):   # get the list of files
            sid = self.pattern.parser(fn)
            if not sid.isnumeric(): continue
            self.studentList.append(sid)
            file = os.path.join(self.srcDir, fn)
            if zipfile.is_zipfile(file): # if it is a zipfile, extract it
                with zipfile.ZipFile(file) as item: # treat the file as a zip
                    item.extractall(os.path.join(self.destDir, sid))  # extract it in the working directory
        self.extracted = True
    
    def getStudentList(self):
        if not self.extracted: 
            print("Please call extract() first.")
            return None
        return self.studentList
    
    def getCodeDirPath(self,sid):
        if not self.extracted: 
                print("Please call extract() first.")
                return None
        for dir,_,files in os.walk(os.path.join(self.destDir, sid)):
            if self.featureFiles and all(fF in files for fF in self.featureFiles): return dir
        return None

    def getCodeFilePath(self,sid,watchFile):
        if not self.extracted: 
                print("Please call extract() first.")
                return None
        for dir,_,files in os.walk(os.path.join(self.destDir, sid)):
            for file in files:
                if file==watchFile: return os.path.join(dir, file)
        return None