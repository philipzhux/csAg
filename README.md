# CUHK CS Automated Grading Tools

## Usage

### Grading

```Python
from cuhk_ag.pattern import Pattern
from cuhk_ag.grader import Grader
from cuhk_ag.extract import Extracter
import os
if __name__ == "__main__":
    # format of "XXXX_119010486_XXXX_XXX_..." can be defined as ("{}_{}_{}",1)
    # format of "XXXX_XX_119010486_XXX_..." can be defined as ("{}_{}_{}_{}",2)
    pattern = Pattern(format=("{}_{}_{}", 1))
    extracter = Extracter(featureFiles=["hw2.cpp"],
                          srcDir="/Users/philip/dev/gradebook_CSC315022103207_Assignment202_2022-11-12-22-08-00",
                          destDir="/tmp/a2/", pattern=pattern)

    def compiling(workplace_path):
        print(workplace_path)
        return os.path.join(workplace_path, "a.out")

    def running(executable_path):
        print(executable_path)
        return f"echo {executable_path}"

    def grading(run_output_path):
        print(run_output_path)
        return 100
    grader = Grader(concernFiles=["hw2.cpp"], compiling=compiling, running=running,
                    grading=grading, scoreJSON="./score.json", extractor=extracter)
    grader.compileAll()
    grader.runAll()
    grader.gradeAll(manual=False)
    grader.saveScore()
```

### Plagiarism checker

```Python
from cuhk_ag.pattern import Pattern
from cuhk_ag.extract import Extracter
from cuhk_ag.mosser import Mosser
from cuhk_ag.concat import Concater
import os
if __name__ == "__main__":
    # format of "XXXX_119010486_XXXX_XXX_..." can be defined as ("{}_{}_{}",1)
    # format of "XXXX_XX_119010486_XXX_..." can be defined as ("{}_{}_{}_{}",2)
    pattern = Pattern(format=("{}_{}_{}", 1))
    extracter = Extracter(featureFiles=["hw2.cpp"],
                          srcDir="/Users/philip/dev/gradebook_CSC315022103207_Assignment202_2022-11-12-22-08-00",
                          destDir="/tmp/a2/", pattern=pattern)
    concater = Concater(destDir="./concat/",concernFiles=["hw2.cpp"],extracter=extracter)
    concater.concat(output_extension="cpp")
    mosser = Mosser(srcDir="./concat/", language="cc", extension="cpp",
                    studentList=extracter.getStudentList(), templateFile="/tmp/source/hw2.cpp")
    # mosser.setResultUrl("http://moss.stanford.edu/results/9/419110195684")
    mosser.runMoss()
    mosser.parseMoss()
    mosser.printRes()
    mosser.getSuspectedStudents(threshold=38)

```

TODO: More documentations and possibly bug fixes
