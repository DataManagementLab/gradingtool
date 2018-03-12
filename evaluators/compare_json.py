import json
import os


def compare_json(input_folder, exercise_folder, params=None):
    """
    Compares an input file line by line with a reference file and counts the correct line

    :param input_folder: folder containing the submission
    :param exercise_folder: folder containing the current exercise
    :param params: additional parameters - should contain filename and reference_file
    :return: points, comment
    """

    points = 0
    comment = ""

    for f in params['filenames']:
        input_f = os.path.join(input_folder, "application", f)
        if not os.path.exists(input_f):
            comment += f"{f}: File missing. "
            break
        with open(input_f) as input_file, open(os.path.join(exercise_folder, f)) as reference_file:
            user_file_json = json.load(input_file)
            reference_json = json.load(reference_file)

            if len(user_file_json) < len(reference_json):
                comment += f"{f}: Entries missing. "
            elif len(user_file_json) > len(reference_json):
                comment += f"{f}: Too many entries. "
            else:
                reference_dict = {}
                for ref_entry in reference_json:
                    reference_dict[ref_entry["userName"]] = set(ref_entry["mostVisited"])

                for user_entry in user_file_json:
                    if reference_dict[user_entry["userName"]] != set(user_entry["mostVisited"]):
                        comment += f"{f}: Returned wrong favorites. "

        points += params['points']

    return points, comment.rstrip()


if __name__ == "__main__":
    p, c = compare_json("../sample/output/91", "../sample/exercise/", {'filenames': ['favorites_small.json', 'favorites_big.json'], 'points': 4.5})
    print(p)
    print(c)
