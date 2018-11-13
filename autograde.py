import argparse
import importlib
import json
import os
import shutil
import zipfile
import patoolib


def run_evaluation(name, input_folder, exercise_folder, total_points, params=None):
    """
    Call evaluation function with the given name

    :param name: name of the evaluation function to call
    :param input_folder: folder containing the submission to evaluate
    :param exercise_folder: folder containing the current exercise
    :param total_points: maximum of points that can be reached in this task
    :param params: additional parameters for evaluation function
    :return: points archived, additional comment/error message/...
    """
    if params is None:
        params = {}
    params["total_points"] = total_points

    # Run evaluator on subfolder if specified in task description
    if "subfolder" in params:
        input_folder = os.path.join(input_folder, params["subfolder"])

    evaluation_mod = importlib.import_module("evaluators."+name)
    evaluation_function = getattr(evaluation_mod, name)
    return evaluation_function(input_folder, exercise_folder, params)


def flatten(current_path, base_path=None):
    """
    Flatten folder structure

    :param current_path: current path for recursive walking
    :param base_path: target folder (if None, current folder is target folder -- starting folder of recursion)
    """
    if base_path is None:
        base_path = current_path
    for file_or_dir in os.listdir(current_path):
        file_or_dir_fullpath = os.path.join(current_path, file_or_dir)
        if os.path.isfile(file_or_dir_fullpath):
            if current_path != base_path:
                try:
                    shutil.move(file_or_dir_fullpath, base_path)
                except shutil.Error:
                    print(f"Could not move file {file_or_dir_fullpath}")
        else:
            flatten(os.path.join(current_path, file_or_dir), base_path)


# Command line interface
parser = argparse.ArgumentParser(description='Grade submissions')
parser.add_argument('exercise', metavar='exercise', type=str, nargs=1,
                    help='config folder of the exercise')
parser.add_argument('submissions', metavar='submissions', type=str, nargs=1,
                    help='folder containing the submissions')
parser.add_argument('output', metavar='output', type=str, nargs=1,
                    help='output folder (will contain grade table, unziped files, test run results, ...')
parser.add_argument('--skip-unzip', dest='skip_unzip', action='store_const',
                    const=True, default=False,
                    help='Skip unzip process')
parser.add_argument('--skip-flatten', dest='skip_flatten', action='store_const',
                    const=True, default=False,
                    help='Skip flatten of submission (removal of folders)')

args = parser.parse_args()

exercise_folder = args.exercise[0]
submission_folder = args.submissions[0]
output_folder = args.output[0]


# Create output folder if needed
if not os.path.exists(output_folder):
    os.makedirs(output_folder)


# Unzip submissions and store the contentes in output folder
if not args.skip_unzip:
    submission_files = os.listdir(submission_folder)
    for sf in submission_files:
        input_file = os.path.join(submission_folder, sf)
        # Get group name from submission file name
        output_name = sf.split("-")[0]
        output_folder_submission = os.path.join(output_folder, output_name)

        # Already present? Skip
        if not os.path.isdir(output_folder_submission):
            # Either unzip...
            if sf.endswith(".zip"):
                zipfile.ZipFile(input_file).extractall(output_folder_submission)
            # ... or unrar
            elif sf.endswith(".rar"):
                if not os.path.exists(output_folder_submission):
                    os.makedirs(output_folder_submission)
                patoolib.extract_archive(input_file, outdir=output_folder_submission)
            # Visit the newly created folder (if any) and flatten if necessary
            if not args.skip_flatten and os.path.isdir(output_folder_submission):
                flatten(output_folder_submission)


# Load task config
with open(os.path.join(exercise_folder,'tasks.json')) as tasks_file:
    tasks = json.load(tasks_file)


# For every submission...
submissions = [os.path.join(output_folder, sfolder) for sfolder in os.listdir(output_folder)]
for submission in submissions:
    if os.path.isdir(submission):
        print(submission)
        results = []
        # ...and every task:
        for task in tasks:
            # Auto-graded task?
            if not task["manually"]:
                # Perform evaluation
                points, comment = run_evaluation(task["evaluator"], submission, exercise_folder, task["total_points"], task["params"])
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
