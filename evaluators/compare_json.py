import json
import os


def compare_json(input_folder, exercise_folder, params=None):
    """
    Compares two json files using knowledge about their internal structure

    Currently, this is really targeted at the favorites json structure

    :param input_folder: folder containing the submission
    :param exercise_folder: folder containing the current exercise
    :param params: additional parameters - should contain filename and reference_file
    :return: points, comment
    """

    points = 0
    comment = ""

    for f in params['filenames']:
        input_f = os.path.join(input_folder, f)
        if not os.path.exists(input_f):
            comment += f"Could not create {f} due to syntax or import error(s).\n"
            continue
        with open(input_f) as input_file, open(os.path.join(exercise_folder, f)) as reference_file:
            user_file_json = json.load(input_file)
            reference_json = json.load(reference_file)

            error = False

            reference_names = set(e["userName"] for e in reference_json if "userName" in e and "mostVisited" in e and len(e["mostVisited"]) > 0)
            user_names = set(e["userName"] for e in user_file_json if "userName" in e and "mostVisited" in e and len(e["mostVisited"]) > 0)

            if len(user_names) < len(reference_names):
                comment += f"{f}: Entries missing.\n"
                error = True
            elif len(user_names) > len(reference_names):
                comment += f"{f}: Too many entries.\n"
                error = True
            else:
                reference_dict = {}
                for ref_entry in reference_json:
                    reference_dict[ref_entry["userName"]] = set(ref_entry["mostVisited"])

                for user_entry in user_file_json:
                    if "userName" not in user_entry or "mostVisited" not in user_entry:
                        comment + f"{f}: Invalid format.\n"
                        error = True
                    else:
                        user_name = user_entry["userName"]
                        if user_name not in reference_dict or reference_dict[user_name] != set(user_entry["mostVisited"]):
                            comment += f"{f}: Returned wrong favorites.\n"
                            error = True
                            break

            if not error:
                points += params['points']

    return points, comment.rstrip()


if __name__ == "__main__":
    p, c = compare_json("../sample/output/91", "../sample/exercise/", {'filenames': ['favorites_small.json', 'favorites_big.json'], 'points': 4.5})
    print(p)
    print(c)
