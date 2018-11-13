import json
import sys


class MergeConflict(Exception):
    def __init__(self, message):
        super().__init__(message)


def read_json_file(filename):
    data = None
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def write_json_file(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=2)


def same_fields(dict1, dict2, fields):
    for f in fields:
        if dict1[f] != dict2[f]:
            return False
    return True


def results_writer(results_file_name, results, tasks, force_overwrite=True):
    if force_overwrite:
        write_json_file(results_file_name, results)
        return

    # if we have no old file, write results directly
    old_results = None
    try:
        old_results = read_json_file(results_file_name)
    except FileNotFoundError:
        write_json_file(results_file_name, results)
        return

    # check all tasks and merge old and new results
    for i in range(len(tasks)):
        if not same_fields(tasks[i], old_results[i], ['name', 'total_points']):
            raise MergeConflict("Tasks and Results do not match by 'name' or 'total_points'")

        if not same_fields(old_results[i], results[i], ['name', 'points', 'total_points', 'comment']):
            # Never overwrite manually graded fields
            if tasks[i]['manually']:
                results[i] = old_results[i]
                continue

            # Do specialized merging here
            print(f"[INFO]: \"{results_file_name}\" updated task: {tasks[i]['name']}", file=sys.stderr)

    # write merged results
    write_json_file(results_file_name, results)
