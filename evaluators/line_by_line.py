import os


def line_by_line(input_folder, exercise_folder, params=None):
    """
    Compares an input file line by line with a reference file and counts the correct line

    :param input_folder: folder containing the submission
    :param exercise_folder: folder containing the current exercise
    :param params: additional parameters - should contain filename and reference_file
    :return: points, comment
    """

    points = 0
    comment = ""

    input_file_name = os.path.join(input_folder, params['filename'])
    reference_file_name = os.path.join(exercise_folder, params['reference'])

    if not os.path.exists(input_file_name):
        comment = "No submission for this task"
    else:
        # Open input file and reference file
        with open(input_file_name) as input_file, open(reference_file_name) as reference_file:
            # Loop over every line
            for i, (input_line, reference_line) in enumerate(zip(input_file, reference_file)):
                # Lines match? Increase points
                if input_line.strip() == reference_line.strip():
                    points += 1
                # Otherwise, create a comment, stating which line was wrong
                else:
                    comment += "Wrong answer for {}), should be {}. ".format(chr(97+i), reference_line.strip())

    return points, comment.rstrip()


if __name__ == "__main__":
    p, c = line_by_line("../sample/output/91", "../sample/exercise/", {'filename': 'answer_1.txt', 'reference': 'reference_1.txt'})
    print(p)
    print(c)
