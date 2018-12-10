import os
import subprocess
import re
import shlex
from shutil import copyfile
from utils import robust_filereader


def prepareStudentCode(input_file):
    """
    Prepare the student code for compiliation
    This removes umlauts from the code to avoid compilation/encoding errors
    It also removes "System.out.print" statements to prevent code from running too long.
    The original file will be backed up as .back file

    :param input_file: The file (path) which to prepare
    """
    if not os.path.exists(input_file):
        print("The following path does not exists", input_file)
        return False
    # backup origFile
    copyfile(input_file,input_file+".back")

    # fileHandleRead = open(input_file, 'r')
    # code = fileHandleRead.read()
    code = robust_filereader(input_file, as_lines=False, fix_nls=True)
    #remove Umlauts from the code
    for ch in ['Ä', 'ä','Ö','ö','ü','Ü','ß']:
        if ch in code:
            code = code.replace(ch,'@')
    code = code.replace('System.out.print','//System.out.print')
    # fileHandleRead.close()
    fileHandleWrite = open(input_file, 'w')
    fileHandleWrite.write(code)
    fileHandleWrite.close()


def checkForString(input_file, checkString):
    """
    Determines whether the given string appears in the given file or not

    :param input_file: The file (path) in which to check for appreance of string
    :param checkString: String which has to appear in the input_file
    :return boolean, true if checkString appears in input_file, false otherwise
    """
    checkResult = False
    if not os.path.exists(input_file):
        print("The following path does not exists", input_file)
        return False
    # fileHandle = open(input_file)
    # code = fileHandle.read()
    robust_filereader(input_file, as_lines=False, fix_nls=True)
    m = re.search('.*'+checkString+'.*', code)
    if m:
        #print("Match",m.group(0))
        checkResult = True
        # TODO
        # if the string is surrounded in a comment then we assume it is not used
        m1 = re.search('//.*'+checkString+'.*', code)
        # If we have multiple multi-line comments this will match everything
        # Student are supposed to complain until better solution has been found
        m2 = re.search('.*@Override[\s\S]*/\*([\s\S]*?'+checkString+'[\s\S]*?)\*/', code)
        if m1 or m2:
            #print("Match1",m1.group(0))
            #print("Match2",m2.group(0))
            checkResult = False

    return checkResult

def parseTestResult(result_file, test_name=""):
    """
    Parses a result file and determines points and potential error messages

    :param result_file: The result file to parse/evaluate
    :return points, comment
    """

    fileHandle = open(result_file)
    resultLines = fileHandle.readlines()
    #print(resultLines)
    #parse how many test failed / passed
    resultLine = resultLines[len(resultLines)-2]
    m = re.search('OK \((\d+) tests\)', resultLine)
    #print("'"+resultLine+"'")
    comment = ""
    if m:
        return int(m.group(1)), f"{test_name}: passed\n"
    else:
        m = re.search('Tests run: (\d+),  Failures: (\d+)', resultLine )
        if m:
            total = int(m.group(1))
            failed = int(m.group(2))
            comment += f"{test_name} failed\n"
            for idx,line in enumerate(resultLines):
                if re.match("^\d+\)", line, re.MULTILINE):
                    comment += line + resultLines[idx+1]

            return (total - failed), comment
        else:
            m = re.search('Exception in thread "main" (.*)', resultLines[1])
            if m:
                return 0, f"{test_name}: {m.group(1)}"
            else:
                print("Unexpected result, pls. check following file", result_file)
                return 0, f"{test_name}: Pls. check with instructors\n"

def junitEvaluatorWithContentTest(input_folder, exercise_folder, params=None):
    """
    Compiles student code and calls junit test for an problem

    :param input_folder: folder containing the submission
    :param exercise_folder: folder containing the current exercise
    :param params: additional parameters - should contain filename and reference_file
    :return: points, comment
    """

    points = 0
    comment = ""
    classpathSeperator = ':'

    if os.name == 'nt':
        classpathSeperator = ';'

    stop = False
    java_files = ''
    for f in params['java_files']:
        java_file = os.path.join(input_folder,f)
        if os.path.exists(java_file):
            java_files += "'"+java_file + "' "
            # prepare code for automated evaluation
            prepareStudentCode(java_file)

        else:
            comment += f"Missing file {java_file.split('/')[-1]}\n"
            stop = True

    # check if string is in submission
    if 'string_check' in params:
        print("Checking for given string in file",params['string_check'])
        for f,s in params['string_check'].items():
            input_file = os.path.join(input_folder,f)
            if not checkForString(input_file,s):
                comment += f"Mandatory string '{s}' not found in file {f}\n"
                points -= 1

    # create compilation directory
    compileDir = os.path.join(input_folder, "bin/")
    if not os.path.exists(compileDir):
        os.makedirs(compileDir)

    # create log file
    logFile = os.path.join(input_folder, 'logFile.txt')
    fh_logFile = open(logFile, 'a')

    # assemble class path
    classpath = ""
    classpath += os.path.join(exercise_folder, params['testing_jar'])
    classpath += classpathSeperator + os.path.join(exercise_folder, params['junit_jar_path'])
    if 'additional_jars' in params:
        for f in params['additional_jars']:
            classpath += classpathSeperator + os.path.join(exercise_folder, f)

    # compile code
    cmd = params['javac_path'] + ' -d ' +  "'" + compileDir + "'" + ' -cp ' + "'" + classpath + "'" + ' ' + java_files
    print("Running following command: ", cmd)
    fh_logFile.write("Running following command: "+cmd+"\n")
    proc = subprocess.Popen(cmd, shell=True, stdout=fh_logFile, stderr=fh_logFile).wait()
    fh_logFile.close()

    # javac -d <compilation directory> -cp <junit-location>:<test-jar-location> <filenames>
    #e.g.: javac -d bin/ -cp ~/Downloads/junit-4.12.jar:SDM_Exercise_02_Solution.jar SQLInteger.java SQLVarchar.java RowPage.java HeapTable.java

    # We stop after compilation since sometimes following assignments depend on the compiled sources
    if stop:
        comment += "\nPls. check with instructor if necessary.\n"
        return 0, comment.rstrip()

    # extend classpath with compiled submission files
    classpath += classpathSeperator + compileDir
    classpath += classpathSeperator + os.path.join(exercise_folder, params['hamcrest_jar_path'])

    TIMEOUT_TIME = 60
    # run Junit test
    for junit_test in params['junit_test_fqns']:

        resultFile = os.path.join(input_folder, 'result_' + junit_test + '.txt')
        fh_resultFile = open(resultFile, 'a')
        cmd = params['java_path'] + ' -cp ' + "'" + classpath + "'" + ' org.junit.runner.JUnitCore '+ junit_test
        print("Running following command: ", cmd)
        fh_resultFile.write("Running following command: "+cmd+"\n")
        try:
            proc = subprocess.Popen(cmd, shell=True, stdout=fh_resultFile, stderr=fh_resultFile)
            proc.wait(timeout=TIMEOUT_TIME) # wait in seconds
        except subprocess.TimeoutExpired as err:
            print("Catched TimeoutExpired exception after " + str(TIMEOUT_TIME) + " seconds, writing into result file")
            fh_resultFile.write("Exception in thread \"main\": " + str(err))
            print("Killing the child process")
            proc.kill()
        # e.g. java -cp bin/:/Users/melhindi/Downloads/junit-4.12.jar:SDM_Exercise_02_Solution.jar:/Users/melhindi/Downloads/hamcrest-core-1.3.jar org.junit.runner.JUnitCore de.tuda.sdm.dmdb.test.TestSuiteDMDB
        # e.g. java -cp bin/:/Users/melhindi/Downloads/junit-4.12.jar:SDM_Exercise_02_Solution.jar:/Users/melhindi/Downloads/hamcrest-core-1.3.jar org.junit.runner.JUnitCore de.tuda.sdm.dmdb.test.storage.types.TestSQLInteger
        #fileHandle = open(resultFile)
        #resultLines = fileHandle.readlines()
        #print(resultLines)
        p, c = parseTestResult(resultFile, junit_test)
        c = '\n'.join(c.splitlines())
        points += p
        comment += f"{c}\n"
        fh_resultFile.close()

    if points < 0:
        points = 0

    return points, comment.rstrip()


if __name__ == "__main__":
    p, c = junitEvaluatorWithContentTest(".", ".",
            {
  "java_files": ["SQLInteger.java", "SQLVarchar.java"],
  "junit_test_fqns": ["de.tuda.sdm.dmdb.test.storage.types.TestSQLInteger", "de.tuda.sdm.dmdb.test.storage.types.TestSQLVarchar"],
  "testing_jar": "SDM_Exercise_02_Solution.jar",
  "junit_jar_path": "$HOME/Downloads/junit-4.12.jar",
  "hamcrest_jar_path": "$HOME/Downloads/hamcrest-core-1.3.jar",
  "java_path": "/usr/bin/java",
  "javac_path": "/usr/bin/javac",
  "string_check":{"SQLInteger.java":">>"}
})

    print(p)
    print(c)
