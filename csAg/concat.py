from .pattern import Pattern
from .extract import Extracter
import os
class Concater:
    def __init__(self, destDir, concatFiles, extracter):
        os.makedirs(destDir, exist_ok=True)
        self.destDir = destDir
        self.concatFiles = concatFiles
        self.extracter = extracter

    def concat(self, output_extension):
        if not self.extracter.extracted: self.extracter.extract()
        for sid in self.extracter.getStudentList():
            with open(os.path.join(self.destDir,f"{sid}.{output_extension}"),"ab") as outFile:
                for fn in self.concatFiles:
                    # print(fn)
                    inPath = self.extracter.getCodeFilePath(sid,fn)
                    # print(inPath)
                    if inPath:
                        with open (inPath,"rb") as inFile:
                            outFile.write(inFile.read())