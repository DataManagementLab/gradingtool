import argparse
import csv
import json
import os
import locale
import datetime

def probe_locales(locales):
    for l in locales:
        try:
            locale.setlocale(locale.LC_ALL, l)
        except:
            pass
        else:
            return
    raise locale.Error('Could not find correct locale')

probe_locales(['DE', 'de_DE.utf8', 'de_DE.UTF-8'])

timestamp = f"{datetime.datetime.now():%A, %d %B %Y, %H:%M}"


# Command line interface
parser = argparse.ArgumentParser(description='Export grading results in moodle import format')
parser.add_argument('gradingsheet', metavar='gradingsheet', type=str, nargs=1,
                    help='stencil file to fill with results')
parser.add_argument('results', metavar='results', type=str, nargs=1,
                    help='folder containing the results')
parser.add_argument('passing_threshold', metavar='passing_threshold', type=float, nargs=1,
                    help='threshold to pass the exercise (between 0 and 1.0)')
parser.add_argument('--no-pass', metavar='no_pass', type=str, nargs=1,
                    help='specify group numbers that should not pass, comma separated')
args = parser.parse_args()

gradingsheet = args.gradingsheet[0]
results_folder = args.results[0]
passing_threshold = args.passing_threshold[0]

shall_not_pass = set()
if args.no_pass:
    shall_not_pass.update(args.no_pass[0].split(','))


# Load gardingsheet (stencil)
moodle_import_file = open(os.path.join(results_folder, "grades.csv"), 'w')
fieldnames = ["Identifier", "Full name", "Email address", "Status", "Group", "Grade", "Maximum Grade",
              "Grade can be changed", "Last modified (submission)", "Last modified (grade)", "Feedback comments"]


# Prepare writer and write headlines
writer = csv.writer(moodle_import_file, delimiter=',', quotechar='"', lineterminator='\n')
writer.writerow(fieldnames)


def nl2html(comment):
    return comment.strip().replace('\n', '<br>')


# Open result file
with open(gradingsheet, 'r') as csvfile:
    # Read gradingsheet line by line (ignore first line)
    reader = csv.DictReader(csvfile, fieldnames=fieldnames)
    next(reader)

    submission_count = 0
    passed_count = 0

    # For all entries (rows) in csv...
    for row in reader:
        # ...check if there is a submission
        if not row["Status"].startswith("No submission"):
            # Yes? Calculate grade and create comment

            # Check if result of submission exists, this is relevant if we have to re-run the correction for only a few groups
            # Open results of submission
            results_file = os.path.join(results_folder, row["Group"], "results.json")
            if not os.path.exists(results_file):
                continue
            results = json.load(open(results_file, "r"))

            plagiarism = False
            if shall_not_pass and row['Group'].endswith(tuple(shall_not_pass)):
                plagiarism = True

            # Calculate grade
            names = [r["name"] for r in results]
            points = [r["points"] if r["points"] > 0 else 0 for r in results]
            total_points = [r["total_points"] for r in results]
            comments = [nl2html(r["comment"]) for r in results]

            points_scored = sum(points)
            total_points_possible = sum(total_points)
            passed = points_scored / total_points_possible >= passing_threshold
            if plagiarism:
                passed = False
            grade = 1 if passed else 0

            # Combine comment
            comment = "<table>"
            comment += "<tr><th>Task</th><th>Points</th><th>Comment</th></tr>"
            for n, p, tp, c in zip(names, points, total_points, comments):
                comment += f"<tr><td valign=\"top\">{n}</td><td valign=\"top\" align=\"right\">{p}/{tp}</td><td>{c}</td></tr>"
            comment += "</table>"
            comment += f"<br><br>{points_scored}/{total_points_possible} => Passed: {passed}"
            if plagiarism:
                comment += '<br>br>You did not pass because plagiarism was detected.'

            # Set current timestamp
            outputtimestamp = timestamp

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

            submission_count += 1
            if passed:
                passed_count += 1

print(f"Exported results to {moodle_import_file.name}")
print(f"{passed_count}/{submission_count} ({passed_count/submission_count*100:.2f}%) passed.")
