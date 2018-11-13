import os
import sqlite3
import re

from utils import robust_filereader

def sql_query(input_folder, exercise_folder, params=None):
    """
    Compare the results of sql statements to reference statements

    :param input_folder: folder containing the submission
    :param exercise_folder: folder containing the current exercise
    :param params: additional parameters - should contain filename and reference_file
    :return: points, comment
    """

    points = 0
    comment = ""

    # Get file paths
    input_file_name = os.path.join(input_folder, params['filename'])
    db = os.path.join(exercise_folder, params['db'])
    reference_file_name = os.path.join(exercise_folder, params['reference'])
    points_file_name = os.path.join(exercise_folder, params['points'])

    # Is there a submission?
    if not os.path.exists(input_file_name):
        comment = "No submission for this task\n"
    else:
        # Connect to database
        conn = sqlite3.connect(db)
        c = conn.cursor()

        # Open input file, reference file & pointing schema
        with open(points_file_name) as points_file:
            # Extract queries from submission and reference file
            queries_student = get_queries(input_file_name, params['query_count'])
            queries_reference = get_queries(reference_file_name, params['query_count'])

            # Load pointing schema
            max_points = []
            for line in points_file:
                max_points.append(int(line))

            # Loop over all queries
            for i, (query_student, query_reference, p) in enumerate(zip(queries_student, queries_reference, max_points)):
                # Is there a query for this subtask?
                if query_student is not None:
                    try:
                        # Try to execute it...
                        c.execute(query_student)
                        result_student = c.fetchall()
                        c.execute(query_reference)
                        result_reference = c.fetchall()

                        # And compare it to the reference
                        if result_student == result_reference:
                            # Correct? Give the points
                            points += p
                        else:
                            # No complete match? Try to assess the difference automatically and write a comment
                            if len(result_reference) > len(result_student):
                                comment += f"{i+1}) Results missing\n"
                            elif len(result_reference) < len(result_student):
                                comment += f"{i+1}) Too many results\n"
                            else:
                                comment += f"{i+1}) Wrong results or wrong order\n"
                    except sqlite3.OperationalError:
                        comment += f"{i+1}) Invalid syntax.\n"

    return points, comment.rstrip()


def get_queries(sql_file_name, query_count):
    """
    Extract queries from file

    :param sql_file: file containing queries
    :param query_count: count of queries in file
    :return: list of queries, may contain None if query was not present
    """
    queries = [None] * query_count
    current_query = ""
    current_query_id = -1

    # Parse file line by line
    for line in robust_filereader(sql_file_name, as_lines=True, try_naive=True):
        # Ignore comments
        if not line.startswith("--"):
            # Find markers for new queries
            if line.startswith(".shell echo"):
                # New query that needs to be stored?
                if current_query_id > -1:
                    # Store query in list of queries while removing the ";" in the end and trimming whitespace
                    queries[current_query_id] = current_query.replace(";", "").strip()
                    current_query = ""
                # Get ID for query starting in the next line
                ids = re.findall(r'\d+', line)
                current_query_id = int(ids[0]) - 1 if len(ids) > 0 else -1
            else:
                # Combine multi-line queries (remove additional whitespace)
                current_query += " " + line.strip()

    return queries


if __name__ == "__main__":
    p, c = sql_query("../sample/output/Gruppe 91", "../sample/exercise/", {'filename': 'answer_2_2.sql', 'reference': 'solution_2_2.sql', 'db': 'sdm_exercise1.db', 'query_count': 10, 'points':'points_2_2.txt'})
    print(p)
    print(c)
