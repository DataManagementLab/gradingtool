import argparse
import os
import imp
import rarfile
import zipfile
import json
import re
import sys
import csv

reload(sys)
sys.setdefaultencoding('utf8')

# used to flatten a up archive: https://stackoverflow.com/questions/8689938/extract-files-from-zip-without-keep-the-top-level-folder-with-python-zipfile
def get_members(zip):
    parts = []
    # get all the path prefixes
    for name in zip.namelist():
        # only check files (not directories)
        if not name.endswith('/'):
            # keep list of path elements (minus filename)
            parts.append(name.split('/')[:-1])
    # now find the common path prefix (if any)
    prefix = os.path.commonprefix(parts)
    if prefix:
        # re-join the path elements
        prefix = '/'.join(prefix) + '/'
    # get the length of the common prefix
    offset = len(prefix)
    # now re-set the filenames
    for zipinfo in zip.infolist():
        name = zipinfo.filename
        # only check files (not directories)
        if len(name) > offset:
            # remove the common prefix
            zipinfo.filename = name[offset:]
            yield zipinfo

def run_evaluation(name, input_folder, exercise_folder, params=None):
    """
    Call evaluation function with the given name

    :param name: name of the evaluation function to call
    :param input_folder: folder containing the submission to evaluate
    :param exercise_folder: folder containing the current exercise
    :param params: additional parameters for evaluation function
    :return: points archived, additional comment/error message/...
    """
    if params is None:
        params = []

    print("Using following input folder '"+input_folder+"'")
    # load python file
    mod_name = os.path.join("./evaluators", name+".py")
    mod = imp.load_source('evaluator', mod_name)
    print("loading module", mod_name)
    # load evaluator method and pass params
    # (input_folder, exercise_folder, params)
    return getattr(mod, name)(input_folder, exercise_folder,params)


# Command line interface
parser = argparse.ArgumentParser(description='Grade submissions')
parser.add_argument('exercise', metavar='exercise', type=str, nargs=1,
                    help='config folder of the exercise')
parser.add_argument('submissions', metavar='submissions', type=str, nargs=1,
                    help='folder containing the submissions')
parser.add_argument('output', metavar='output', type=str, nargs=1,
                    help='output folder (will contain grade table, unziped files, test run results, ...')
parser.add_argument('--plagcheck', dest='plagcheck', action='store_const',
                    const=True, default=False,
                    help='Perform check for plagiarism')

args = parser.parse_args()

exercise_folder = args.exercise[0]
submission_folder = args.submissions[0]
output_folder = args.output[0]


# Initilaize data structure
results = []
# TODO Implement

# Create output folder if needed
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Unzip input files, insert records for every group in result structure
# unzip files
for filename in os.listdir(submission_folder):
    infile = os.path.join(submission_folder, filename)
    outfolder = os.path.join(output_folder, os.path.splitext(filename)[0].replace(" ", "_"))
    if filename.endswith(".zip"):
        zf = zipfile.ZipFile(infile)
        zf.extractall(outfolder, get_members(zf))
        zf.close()
    
    if filename.endswith(".rar"):
        continue
        #rf = rarfile.RarFile(filename)
        #rf.extractall(filename,output_folder)
        #rf.close()

# TODO Implement

# Plagiarism checker
if args.plagcheck:
    print("Running check for plagiarism")
    # TODO Implement

# Load task config
task_file = os.path.join(exercise_folder, 'tasks.json')
with open(task_file) as tasksFH:
    tasks = json.load(tasksFH)

# For every submission...
for submission in os.listdir(output_folder):
    # the participant number is included in the moodle fiename and is required for the offline grade book
    m = re.search('.*_(\d+)_assignsubmission_file.*', submission)
    if m:
        participant_number = m.group(1)
    else:
        print("Could not find participant numnber in "+submission+"! Will skip it!")
        continue

    # initialize grading elements
    submission_folder = os.path.join(output_folder, submission)
    total_points = 0
    submission_feedback = ""

    # ...and every task:
    for task in tasks:
        # Autograded task?
        if not task['manually']:
            # Perform evaluation
            print (task['evaluator'])
            points, comment = run_evaluation(task['evaluator'], submission_folder, exercise_folder, task['params'])
        else:
            # Create placeholder
            points, comment = 0, 'Manually graded task: ' + task['name']

        total_points += points
        submission_feedback += "\n" + task['name'] + ":\n" + comment
        submission_feedback = submission_feedback.replace('\n','\r\n')

    # Write result
    #Identifier,"Full name","Email address",Status,Group,Grade,"Maximum Grade","Grade can be changed","Last modified (submission)","Last modified (grade)","Feedback comments"
    results.append((participant_number, total_points, submission_feedback))


# Write result structure to file
# TODO Implement
result_file = os.path.join(output_folder, 'grading_results.csv')
with open(result_file, "w") as the_file:
    csv.register_dialect("custom", delimiter=" ", skipinitialspace=True)
    writer = csv.writer(the_file, dialect="custom")
    for tup in results:
        writer.writerow(tup)
