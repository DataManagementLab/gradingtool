import argparse
import os


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

    return 0, ""


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
results = None
# TODO Implement

# Create output folder if needed
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Create output files if needed
# TODO Implement

# Unzip input files, insert records for every group in result structure
# TODO Implement

# Plagiarism checker
if args.plagcheck:
    print("Running check for plagiarism")
    # TODO Implement

# Load task config
# TODO Implement

# For every submission...
for submission in []:
    # ...and every task:
    for task in []:
        # Autograded task?
        if not task.manually:
            # Perform evaluation
            points, comment = run_evaluation(task.name, submission, task.params)
        else:
            # Create placeholder
            points, comment = -1, ''
        # Store results in the result structure
        # TODO Implement

# Write result structure to file
# TODO Implement
