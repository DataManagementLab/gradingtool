import argparse
import csv
import json
import os
import locale
import datetime

try:
    locale.setlocale(locale.LC_ALL, 'DE')
except:
    locale.setlocale(locale.LC_ALL, 'de_DE')
timestamp = f"{datetime.datetime.now():%A, %d %B %Y, %H:%M}"


# Command line interface
parser = argparse.ArgumentParser(description='Export grading results in moodle import format')
parser.add_argument('gradingsheet', metavar='gradingsheet', type=str, nargs=1,
                    help='stencil file to fill with results')
parser.add_argument('results', metavar='results', type=str, nargs=1,
                    help='folder containing the results')
parser.add_argument('passing_threshold', metavar='passing_threshold', type=float, nargs=1,
                    help='threshold to pass the exercise (between 0 and 1.0)')
args = parser.parse_args()

gradingsheet = args.gradingsheet[0]
results_folder = args.results[0]
passing_threshold = args.passing_threshold[0]


# Load gardingsheet (stencil)
moodle_import_file = open(os.path.join(results_folder, "grades.csv"), 'w')
fieldnames = ["Identifier", "Full name", "Email address", "Status", "Group", "Grade", "Maximum Grade",
              "Grade can be changed", "Last modified (submission)", "Last modified (grade)", "Feedback comments"]


# Prepare writer and write headlines
writer = csv.writer(moodle_import_file, delimiter=',', quotechar='"', lineterminator='\n')
writer.writerow(fieldnames)


# Open result file
with open(gradingsheet, 'r') as csvfile:
    # Read gradingsheet line by line (ignore first line)
    reader = csv.DictReader(csvfile, fieldnames=fieldnames)
    next(reader)

    # For all entries (rows) in csv...
    for row in reader:
        # ...check if there is a submission
        if not row["Status"].startswith("No submission"):
            # Yes? Calculate grade and create comment

            # Open results of submission
            results_file = os.path.join(results_folder, row["Group"], "results.json")
            results = json.load(open(results_file, "r"))

            # Calculate grade
            points = [r["points"] if r["points"] > 0 else 0 for r in results]
            names = [r["name"] for r in results]
            points_scored = sum(points)
            total_points = [r["total_points"] for r in results]
            total_points_possible = sum(total_points)
            passed = points_scored / total_points_possible >= passing_threshold
            grade = 1 if passed else 0

            # Combine comment
            comment_table  = "<br>".join(f"{n}: {p}/{tp}" for n, p, tp in zip(names, points, total_points))
            comment_table += f"<br>{points_scored}/{total_points_possible} => Passed: {passed}"
            comment_details = "<br>".join(f"{r['name']}: {r['comment']}" for r in results if r['comment'] != "")
            comment = comment_table + "<br><br>" + comment_details

            # Set current timestamp
            outputtimestamp = timestamp
        else:
            # No? Output default values
            grade = 0
            comment = ""
            outputtimestamp = "-"

        # Create and write output line
        outputrow = [
            row["Identifier"],
            row["Full name"],
            row["Email address"],
            row["Status"],
            row["Group"],
            grade,
            row["Maximum Grade"],
            row["Grade can be changed"],
            row["Last modified (submission)"],
            outputtimestamp,
            comment
        ]
        writer.writerow(outputrow)
