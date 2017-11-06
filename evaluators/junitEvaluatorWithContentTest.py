import os
import subprocess
import re

def checkForString(input_file, checkString):
    checkResult = False
    fileHandle = open(input_file)
    code = fileHandle.read()
    m = re.search('.*'+checkString+'.*', code)
    #print("'"+resultLine+"'")
    if m:
        #print("Match",m.group(0))
        checkResult = True
        m1 = re.search('//.*'+checkString+'.*', code)
        m2 = re.search('/\*([\s\S]*?'+checkString+'[\s\S]*?)\*/', code)
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
    if m:
        return int(m.group(1)), test_name + " passed"
    else:
        m = re.search('Tests run: (\d+),  Failures: (\d+)', resultLine )
        if m:
            total = int(m.group(1))
            failed = int(m.group(2))
            return (total - failed), test_name + " failed\n" + fileHandle.read()
        else:
            print("Unexpected result, pls. check following file", result_file)
            return 0, "Pls. check with instructors"

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
            java_files += java_file + ' '

        else:
            comment += "Missing file " + java_file + " "
            stop = True

    # check if string is in submission
    if 'string_check' in params:
        print(params['string_check'])
        for f,s in params['string_check'].items():
            input_file = os.path.join(input_folder,f)
            if not checkForString(input_file,s):
                comment += "Mandatory string '"+s+"'not found in file "+f
                stop = True

    if stop:
        return 0, comment.rstrip()


    # create compilation directory
    compileDir = os.path.join(input_folder, "bin/")
    if not os.path.exists(compileDir):
        os.makedirs(compileDir)

    # compile code
    testing_jar = os.path.join(exercise_folder, params['testing_jar'])
    cmd = params['javac_path'] + ' -d ' + compileDir + ' -cp ' + params['junit_jar_path'] + classpathSeperator + testing_jar + ' ' + java_files
    print("Running following command: ", cmd)
    proc = subprocess.Popen(cmd, shell=True).wait()

    # javac -d <compilation directory> -cp <junit-location>:<test-jar-location> <filenames>
    #e.g.: javac -d bin/ -cp ~/Downloads/junit-4.12.jar:SDM_Exercise_02_Solution.jar SQLInteger.java SQLVarchar.java RowPage.java HeapTable.java

    # run Junit test
    for junit_test in params['junit_test_fqns']:

        resultFile =  os.path.join(input_folder, 'result_' + junit_test + '.txt')
        open(resultFile, 'a').close()
        cmd = params['java_path'] + ' -cp ' + compileDir + classpathSeperator + params['hamcrest_jar_path'] + classpathSeperator +  params['junit_jar_path'] + classpathSeperator + testing_jar + ' org.junit.runner.JUnitCore '+ junit_test + ' > ' + resultFile
        print("Running following command: ", cmd)
        proc = subprocess.Popen(cmd, shell=True).wait()
        # e.g. java -cp bin/:/Users/melhindi/Downloads/junit-4.12.jar:SDM_Exercise_02_Solution.jar:/Users/melhindi/Downloads/hamcrest-core-1.3.jar org.junit.runner.JUnitCore de.tuda.sdm.dmdb.test.TestSuiteDMDB
        # e.g. java -cp bin/:/Users/melhindi/Downloads/junit-4.12.jar:SDM_Exercise_02_Solution.jar:/Users/melhindi/Downloads/hamcrest-core-1.3.jar org.junit.runner.JUnitCore de.tuda.sdm.dmdb.test.storage.types.TestSQLInteger
        fileHandle = open(resultFile)
        resultLines = fileHandle.readlines()
        #print(resultLines)
        p, c = parseTestResult(resultFile, junit_test)
        points += p
        comment += c + "\n"

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
