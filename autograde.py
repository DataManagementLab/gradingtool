import argparse
import imp
import json
import os
import rarfile
import zipfile


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

    # TODO implement
    print("run_evaluation :", name,input_folder,exercise_folder,params)
    fo = imp.load_source('line_by_line', name+".py")
    p, c = fo.line_by_line(input_folder,exercise_folder,params)
    return p,c


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


# Create output folder if needed
if not os.path.exists(output_folder):
    os.makedirs(output_folder)


# Unzip submissions and store the contentes in output folder
submission_files = os.listdir(submission_folder)
for sf in submission_files:
    input_file = os.path.join(submission_folder, sf)
    # Get group name from submission file name
    output_name = sf.split("-")[0]
    output_folder_submission = os.path.join(output_folder, output_name)
    # Either unzip...
    if sf.endswith(".zip"):
        zipfile.ZipFile(input_file).extractall(output_folder_submission)
    # ... or unrar
    elif sf.endswith(".rar"):
        if not os.path.exists(output_folder_submission):
            os.makedirs(output_folder_submission)
        rf = rarfile.RarFile(input_file)
        rf.extract(output_folder_submission)


# Plagiarism checker
if args.plagcheck:
    print("Running check for plagiarism")
    # TODO Implement ??


# Load task config
with open(os.path.join(exercise_folder,'tasks.json')) as tasks_file:
    tasks = json.load(tasks_file)


# For every submission...
submissions = [os.path.join(output_folder, sfolder) for sfolder in os.listdir(output_folder)]
for submission in submissions:
    if os.path.isdir(submission):
        results = []
        # ...and every task:
        for task in tasks:
            # Auto-graded task?
            if not task["manually"]:
                # Perform evaluation
                points, comment = run_evaluation(task["name"], submission, task["params"])
            else:
                # Create placeholder
                points, comment = -1, ''
            # Store intermediate result
            results.append({
                "name": task["name"],
                "points": points,
                "total_points": task["total_points"],
                "comment": comment
                })

        # Write (intermediate) results for this submission to file
        json.dump(results, open(os.path.join(submission, "results.json"), "w"), indent=2)
