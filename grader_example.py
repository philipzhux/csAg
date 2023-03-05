from csAg.pattern import Pattern
from csAg.grader import Grader
from csAg.extract import Extracter
import subprocess
import os
if __name__ == "__main__":
    # format of "XXXX_119010486_XXXX_XXX_..." can be defined as ("{}_{}_{}",1)
    # format of "XXXX_XX_119010486_XXX_..." can be defined as ("{}_{}_{}_{}",2)
    pattern = Pattern(format=("{}_{}_{}", 1))
    extracter = Extracter(featureFiles=["hw2.cpp"],
                          srcDir="/Users/philip/dev/gradebook_CSC315022103207_Assignment202_2022-11-12-22-08-00",
                          destDir="/tmp/a2/", pattern=pattern, skipExtract=False)

    def compiling(workplace_path):
        # callback function
        # workplace_path is the path that featureFiles resides (e.g. hw2.cpp)
        # do compile here like 
        # os.system(f"make -C {workplace_path}")
        # return executable file path
        print(workplace_path)
        return os.path.join(workplace_path, "a.out")

    def running(executable_path):
        # callback function
        # return list of output files for grading cb
        # you can also do something else here
        # for example: 
        # os.system("demsg -c")
        # os.system(f"insmod {executable_path}")
        # os.system("rmmod program2.ko")
        # subprocess.call(f"dmesg | grep program2 > {workspace_path}/output1.txt", shell=True)
        # return ["output1.txt"]
        workspace_path = os.path.dirname(executable_path)
        subprocess.call(f"echo {executable_path}/hello world 1 > {workspace_path}/output1.txt", shell=True)
        subprocess.call(f"echo {executable_path}/hello world 1 > {workspace_path}/output2.txt", shell=True)
        return [f"{workspace_path}/output1.txt",f"{workspace_path}/output2.txt"]

    def grading(run_output_paths):
        # callback function
        # grade according to content of file at run_output_path
        # only useful when gradeAll is called with manual = Flase
        # for example
        # import parse
        # with open(run_output_path,"r") as f:
        #   output = f.readlines()
        # score = 0
        # for line in output:
        #     if "The child process has pid = " in line \
        #     and parse.parse("{}The child process has pid = {}",line)[-1].isnumeric(): score += 10
        for run_output_path in run_output_paths:
            print(run_output_path)
        return 100

    grader = Grader(concernFiles=["hw2.cpp"], compiling=compiling, running=running,
                    grading=grading, scoreJSON="./score.json", extractor=extracter)
    grader.compileAll()
    grader.runAll()
    grader.gradeAll(manual=False)
    grader.saveScore()
