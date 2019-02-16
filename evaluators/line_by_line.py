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
        comment = "No submission for this task\n"
    else:
        # Open input file and reference file
        with open(input_file_name) as input_file, open(reference_file_name) as reference_file:
            # Loop over every line
            for i, (input_line, reference_line) in enumerate(zip(input_file, reference_file)):
                # Lines match? Increase points
                possible_answers = reference_line.split('|')
                for answer in possible_answers:
                    if input_line.strip() == answer.strip(): #reference_line.strip():
                        points += 1
                        break
                    # Otherwise, create a comment, stating which line was wrong
                    else:
                        comment += "Wrong answer for {}), should be {}.\n".format(chr(97+i), reference_line.strip().replace('|',' or '))
                        break

    # One point less than the correct count of lines as you can simply infer the last answer
    if "reduce" in params and params["reduce"]:
        points = points - 1 if points > 0 else 0
    return points, comment.rstrip()


if __name__ == "__main__":
    p, c = line_by_line("../sample/output/91", "../sample/exercise/", {'filename': 'answer_1.txt', 'reference': 'reference_1.txt'})
    print(p)
    print(c)
