# csAg: CUHK CS Automated Grading Tools

## Usage

* Extractor: Extract student submission (zip file) with name of certain format and link the student id with the extracted source. Source files (the directory located by the existence of feature file, in regard of students's directory tree structure) are extracted to destDir/sid. The extractor can be passed to grader to further grade the files.

* Grader: Actually grading the extracted files from extractor. Need to feed three callback functions as the below example indicates.

* Concater: Prepare the extracted files for plagiarism detection when there are multiple source/header files in the code project
  
* Mosser: plagiarism detection and auto generate list of students according to similarity threshold set

TODO: More documentations and possibly bug fixes

## How to start grading

1. Installing prerequisites:
  
  ```shell
    cd csAg
    pip install -r requirements.txt
  ```

2. Copy the template grader_example.py

3. Set up callback functions `compile`, `run`, `grade`:
   * for compile, the input argument is the path where source file/make file resides, you should execute the compile command like `os.system(f"make -C {workplace_path}")` and **return the executable path**. Please make sure you use `workspace_path` in your compile command because there is not gurantee where current working path (pwd) is, unless you cd to `workspace_path`. For script lanuage like python, simply return the path to the script (e.g. `os.path.join(workspace_path,"hw.py")`).
   * for run, the input argument is the return value from compile callback, which should be a executable path, you should run the executable(s) and **redirect the output to one or more file**, and return the list of output files for further grading. Output files should be saved in the same path as `executable_path`, which you can extract by `os.path.dirname`.
   * for grade, the input argument will be the list of output file paths. You should grade the output files according to the grading schemes and return the final scores and optional comment for the grade, for example:
  
     ```python
        # option 1
        return 90
        # option 2
        return {
            "score": 90,
            "comment": "edge case -5; style -5;",
        }
     ```
4. Change params like `isCodePath`, `srcDir`, `destDir`,.... Run the code.

*You may change manual `grader.gradeAll(manual=False)` to True to grade manually. In such case, the output will be printed one by one to STDOUT and you will be prompted to enter the correponding grade*

### Grading

```Python
from csAg.pattern import Pattern
from csAg.grader import Grader
from csAg.extract import Extracter
from csAg.persistent import Persistentizer
import subprocess
import os
if __name__ == "__main__":
    # callback functions setting
    def compile(workplace_path):
        # callback function
        # workplace_path is the path that featureFiles resides (e.g. hw2.cpp)
        # do compile here like 
        # os.system(f"make -C {workplace_path}")
        # return executable file path
        print(workplace_path)
        return os.path.join(workplace_path, "a.out")

    def run(executable_path):
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
        subprocess.call(f"echo {executable_path}/hello world 2 > {workspace_path}/output2.txt", shell=True)
        return [f"{workspace_path}/output1.txt",f"{workspace_path}/output2.txt"]

    def grade(run_output_paths):
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
        return {
            "score": 100,
            "comment": "",
        }

    # format of "XXXX_119010486_XXXX_XXX_..." can be defined as ("{}_{}_{}",1)
    # format of "XXXX_XX_119010486_XXX_..." can be defined as ("{}_{}_{}_{}",2)
    pattern = Pattern(format=("{}_{}_{}", 1))
    # isCodePath: 
    # callable, @param: list: files of a particular path, @return: boolean: whether it is target path
    # example: lambda files: "hw.cpp" in files / lambda files: any(file in files for file in ["hw.cpp","hw.py"])
    extracter = Extracter(isCodePath=lambda files: all(file in files for file in ["hw2.cpp","makefile"]),
                          srcDir="/Users/philip/dev/gradebook_CSC315022103207_Assignment202_2022-11-12-22-08-00",
                          destDir="/tmp/a2/", pattern=pattern)
    # @param scoreJSON: output score JSON file path
    # Persistentizer: save persistent result in case of interruption
    # to reduce repetition, also with a lock to prevent multiple run
    # at the same time.
    with Persistentizer(grader = Grader(compile=compile, run=run,
                    grade=grade, scoreJSON="./score.json", commentJSON="./comment.json", extractor=extracter),
                    sessionId="default", restart=False,forcedStart=False) as grader:
        grader.compileAll()
        grader.runAll()
        # with manual false, grading callback is called to grade
        # otherwise, the program will print student output and 
        # halt to wait for score input, and record the score
        grader.gradeAll(manual=False)
        grader.saveScore()
```

### Plagiarism checker

```Python
from csAg.pattern import Pattern
from csAg.extract import Extracter
from csAg.mosser import Mosser
from csAg.concat import Concater
import os
if __name__ == "__main__":
    # format of "XXXX_119010486_XXXX_XXX_..." can be defined as ("{}_{}_{}",1)
    # format of "XXXX_XX_119010486_XXX_..." can be defined as ("{}_{}_{}_{}",2)
    pattern = Pattern(format=("{}_{}_{}", 1))
    extracter = Extracter(isCodePath=lambda files: all(file in files for file in ["hw2.cpp","makefile"]),
                          srcDir="/Users/philip/dev/gradebook_CSC315022103207_Assignment202_2022-11-12-22-08-00",
                          destDir="/tmp/a2/", pattern=pattern)
    concater = Concater(destDir="./concat/",concatFiles=["hw2.cpp"],extracter=extracter)
    concater.concat(output_extension="cpp")
    mosser = Mosser(srcDir="./concat/", language="cc", extension="cpp",
                    studentList=extracter.getStudentList(), templateFile="/tmp/source/hw2.cpp")
    # mosser.setResultUrl("http://moss.stanford.edu/results/9/419110195684")
    mosser.runMoss()
    mosser.parseMoss()
    mosser.printRes()
    mosser.getSuspectedStudents(threshold=38)

```

