# gradingtool
Python Framework to grade assignment submissions

## usage

### autograding tool
    autograde.py [-h] [--plagcheck] exercise submissions output

    positional arguments:
      exercise		config folder of the exercise
      submissions	folder containing the submissions
      output		output folder (will contain grade table, unziped files, test run results, ...
    
    optional arguments:
      -h, --help	show this help message and exit
      --plagcheck	Perform check for plagiarism


### moodle export
    export_to_moodle.py [-h] gradingsheet results passing_threshold

    positional arguments:
      gradingsheet       stencil file to fill with results
      results            folder containing the results
      passing_threshold  threshold to pass the exercise (between 0 and 1.0)

    optional arguments:
      -h, --help         show this help message and exit