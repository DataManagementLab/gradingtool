import argparse
import os,sys
import json
from pprint import pprint
import zipfile,fnmatch
import imp,rarfile,csv
import re

def run_evaluation(name, input_folder, exercise_folder, params=None):
    """
    Call evaluation function with the given name

    :param name: name of the evaluation function to call
    :param input_folder: folder containing the submission to evaluate
    :param exercise_folder: folder containing the current exercise
    :param params: additional parameters for evaluation function
    :return: points archived, additional comment/error message/...
    """
    if params is None:
        params = []

    # TODO implement
    print("run_evaluation :", name,input_folder,exercise_folder,params)
    fo = imp.load_source('line_by_line', name+".py")
    p, c = fo.line_by_line(input_folder,exercise_folder,params)
    return p,c


#input, output file name
output_file_name = 'Results.csv'
input_file_name = 'Grades-SDM WS 201718-Assignment 01 -- Submission-9529.csv'
input_folder_path = u'/home/ehsan/Desktop/SDM_TA/test_ex_02/input/'

# Command line interface
parser = argparse.ArgumentParser(description='Grade submissions')
parser.add_argument('exercise', metavar='exercise', type=str, nargs=1,
                    help='config folder of the exercise')
parser.add_argument('submissions', metavar='submissions', type=str, nargs=1,
                    help='folder containing the submissions')
parser.add_argument('output', metavar='output', type=str, nargs=1,
                    help='output folder (will contain grade table, unziped files, test run results, ...')
parser.add_argument('--plagcheck', dest='plagcheck', action='store_const',
                    const=True, default=False,
                    help='Perform check for plagiarism')

args = parser.parse_args()

exercise_folder = args.exercise[0]
submission_folder = args.submissions[0]
output_folder = args.output[0]

reload(sys)
sys.setdefaultencoding('utf8')

# Initilaize data structure
results = None
# TODO Implement ??

# Create output folder if needed
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Create output files if needed
# TODO Implement ??

# Unzip input files, insert records for every group in result structure
print("------------------------------------------------")
print("start of extraction")
print("------------------------------------------------")
rootPath = submission_folder
pattern = '*.zip'
for root, dirs, files in os.walk(rootPath):
    for filename in fnmatch.filter(files, pattern):
	f_path = os.path.join(root, filename)
	temp_index = f_path.find('_assignsubmission')
	tem_str = f_path[:temp_index]
	print(tem_str)
        #print(os.path.join(root, os.path.splitext(filename)[0]))
        #zipfile.ZipFile(os.path.join(root, filename)).extractall(os.path.join(root, tem_str))
	zipfile.ZipFile(os.path.join(root, filename)).extractall(tem_str)

pattern = '*.rar'
for root, dirs, files in os.walk(rootPath):
    for filename in fnmatch.filter(files, pattern):
	tf_path = os.path.join(root, filename)
	temp_index = f_path.find('_assignsubmission')
	tem_str = f_path[:temp_index]
	print(os.path.join(root, tem_str))
	print("raaaaaaaaaaaaaaaar:"+tem_str)
	print(os.path.join(root, tem_str))
	if not os.path.exists(os.path.join(root, tem_str)):
    		os.makedirs(os.path.join(root, tem_str))
	rf = rarfile.RarFile(os.path.join(root, filename))
        rf.extract(os.path.join(root, tem_str))

# TODO Implement, insert records for every group in result structure ??

# Plagiarism checker
if args.plagcheck:
    print("Running check for plagiarism")
    # TODO Implement ??

# Load task config
# TODO Implement
with open(os.path.join(exercise_folder,'tasks.json')) as config_file:    
    config_data = json.load(config_file)

#iput_abs_path = os.path.abspath("input")
#print(iput_abs_path)
#submissions = [os.path.abspath(name) for "/input/"+ name in os.listdir(iput_abs_path + "/.")]
#dirs = [d for d in os.listdir('input') if os.path.isdir(os.path.join('input', d))]

print("------------------------------------------------")
print("start of greading")
print("------------------------------------------------")

f_writ = open(output_file_name, 'wb')
fieldnames = ["Identifier", "Full name","Email address", "Status","Group","Grade","Maximum Grade","Grade can be changed","Last modified (submission)","Last modified (grade)","Feedback comments"]
writer = csv.writer(f_writ, delimiter=',',
                lineterminator='\r\n',
                quotechar = "'"
                )
with open(input_file_name, 'r') as csvfile:
	reader = csv.DictReader(csvfile, fieldnames=fieldnames)
	for row in reader:
		folder_name = row["Group"]+"-"+row["Full name"]+"_"+row["Identifier"][12:]
		print((os.path.join(submission_folder,folder_name)))
		print(os.path.isdir(os.path.join(submission_folder,folder_name)))		
		if os.path.isdir(os.path.join(submission_folder,folder_name)):
			print(folder_name+"	"+row["Identifier"])
			total_mark=0
			total_comment=''
			for i in config_data:
				print i['params']
				#print("evaluators/" + i['evaluator'])
				#print("input/" + folder_name)
				p,c = run_evaluation(exercise_folder + i['evaluator'],input_folder_path + folder_name,"exercise",i['params'])
				total_mark+=p
				total_comment+=c
			print(total_mark,total_comment)
			row["Grade"]=total_mark
			row["Feedback comments"]=total_comment
			writer.writerow(['\"'+row["Identifier"]+'\"','\"'+row["Full name"]+'\"',row["Email address"],'\"'+row["Status"]+'\"','\"'+row["Group"]+'\"',row["Grade"],row["Maximum Grade"],row["Grade can be changed"],'\"'+row["Last modified (submission)"]+'\"',row["Feedback comments"]])
	

	"""
	for i in config_data:
		for dr in dirs:
			matchObj = re.match( r'Gruppe (.*)-(.*)_(.*)', dr, re.M|re.I)
			test2 = matchObj.group(2)
			mrt_i =test2.find("_")
			Participant_id=test2[mrt_i+1:]
			Participant_id="Participant "+Participant_id[:Participant_id.find("_")]
			#print(Participant_id)
			with open(input_file_name, 'r') as csvfile:
				reader = csv.DictReader(csvfile, fieldnames=fieldnames)
				for row in reader:
					#print("row_var:"+row["Identifier"])
					if Participant_id == row["Identifier"]:
						print i['name']
						#print(row)
						p,c = run_evaluation("evaluators/line_by_line.py","input/Gruppe 14-assignment submission_17889651","exercise",{'filename': 'answer_1.txt', 'reference': 'reference_1.txt'})
						#print(p,c)
						
"""

						

"""
	for row in reader:
		if name == row["Identifier"]:
			print(row)
			writer.writerow(['\"'+row["Identifier"]+'\"','\"'+row["Full name"]+'\"',row["Email address"],'\"'+row["Status"]+'\"','\"'+row["Group"]+'\"',row["Grade"],row["Maximum Grade"],row["Grade can be changed"],'\"'+row["Last modified (submission)"]+'\"',row["Feedback comments"]])


f_writ.close()"""

"""
for i in config_data:
#    print i['name']
	for dr in dirs:
		if(os.path.isfile(iput_abs_path + "/" + dr + "/"+i['params']["filename"])):
			#print("evaluators/" + i['evaluator'],"input/" + dr,"exercise",i['params'], dr[:10],iput_abs_path + "/" + dr + "/"+i['params']["filename"])
			results[results.index([dr[:10]])].append([run_evaluation("evaluators/" + i['evaluator'],"input/" + dr,"exercise",i['params'])])
			#print(dr[:10],results.index([dr[:10]]))
"""

"""
# For every submission...
for submission in []:
    # ...and every task:
    for task in []:
        # Autograded task?
        if not task.manually:
            # Perform evaluation
            points, comment = run_evaluation(task.name, submission, task.params)
        else:
            # Create placeholder
            points, comment = -1, ''
        # Store results in the result structure
        # TODO Implement
"""
# Write result structure to file
# TODO Implement
