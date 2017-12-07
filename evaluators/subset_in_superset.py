import os


def subset_in_superset(input_folder, exercise_folder, params=None):
    """
    Compares a subset in the input file with a superset in the reference file
    Each line represents a set. The separator of the set elements can be configured by setting params['separator']

    :param input_folder: folder containing the submission
    :param exercise_folder: folder containing the current exercise
    :param params: additional parameters - should contain separator (simple char) and elements_in_lines (comma sperated line of integers (json array), e.g., [6,4,1])
    :return: points, comment
    """

    points = 0
    comment = ""

    required_params = ['filename', 'reference', 'separator', 'elements_in_lines']
    for param in required_params:
        if param not in params:
            print("!!!!!!!WARNING!!!!!!!\nPlease set the parameter '" + param +"' in the 'params' object of the corresponding task config in your tasks.json\n")

    input_file_name = os.path.join(input_folder, params['filename'])
    reference_file_name = os.path.join(exercise_folder, params['reference'])

    if not os.path.exists(input_file_name):
        comment = "No submission for this task"
    else:
        # Open input file and reference file
        with open(input_file_name) as input_file, open(reference_file_name) as reference_file:
            # Loop over every line
            for i, (input_line, reference_line) in enumerate(zip(input_file, reference_file)):
                # create sub- (student input file) and super set (reference file)
                student_set = [x.strip() for x in input_line.split(params['separator'])]
                reference_set = [x.strip() for x in reference_line.split(params['separator'])]

                # check that student set is subset of the reference_set
                # i.e., that each element of the student set is contained in the reference set
                # with elements_in_line, we test that students only have the exepcted number of results
                for index in range(0,params['elements_in_lines'][i]):
                    if index < len(student_set):
                        if student_set[index] in reference_set:
                            points += 1
                        # Otherwise, create a comment, stating which element was wrong
                        else:
                            comment += "Wrong answer " +  student_set[index] +"! "

    # One point less than the correct count of lines as you can simply infer the last answer
    if "reduce" in params and params["reduce"]:
        points = points - 1 if points > 0 else 0
    return points, comment.rstrip()


if __name__ == "__main__":
    p, c = line_by_line("../sample/output/91", "../sample/exercise/", {'filename': 'answer_1.txt', 'reference': 'reference_1.txt'})
    print(p)
    print(c)
