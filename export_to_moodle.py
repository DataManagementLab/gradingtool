import argparse
import csv
import os


# Command line interface
parser = argparse.ArgumentParser(description='Export grading results in moodle import format')
parser.add_argument('gradingsheet', metavar='gradingsheet', type=str, nargs=1,
                    help='stencil file to fill with results')
parser.add_argument('results', metavar='results', type=str, nargs=1,
                    help='folder containing the results')
parser.add_argument('results', metavar='results', type=str, nargs=1,
                    help='folder containing the results')

args = parser.parse_args()

gradingsheet = args.gradingsheet[0]
results_folder = args.results[0]


moodle_import_file = open(os.path.join(results_folder, "grades.csv"), 'w')
fieldnames = ["Identifier", "Full name","Email address", "Status","Group","Grade","Maximum Grade","Grade can be changed","Last modified (submission)","Last modified (grade)","Feedback comments"]
writer = csv.writer(moodle_import_file, delimiter=',',
                    lineterminator='\r\n',
                    quotechar = "'"
                    )

with open(gradingsheet, 'r') as csvfile:
    reader = csv.DictReader(csvfile, fieldnames=fieldnames)
    for row in reader:
            row["Grade"]=0
            row["Feedback comments"]=""
            writer.writerow(['\"'+row["Identifier"]+'\"','\"'+row["Full name"]+'\"',row["Email address"],'\"'+row["Status"]+'\"','\"'+row["Group"]+'\"',row["Grade"],row["Maximum Grade"],row["Grade can be changed"],'\"'+row["Last modified (submission)"]+'\"',row["Feedback comments"]])

