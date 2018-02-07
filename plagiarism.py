import os, sys, json
import shutil
import mosspy
from bs4 import BeautifulSoup
import re, csv
import argparse

def Check(output,plagiarism_base_folder,exercise_folder,plagiarism_folder,threshold):
    #output = "output"
    #plagiarism_folder = "plagiarism_output_folder"
    #plagiarism_base_folder = "base"
    #exercise_folder = "exercise"
    #threshold = 20

    if not os.path.exists(plagiarism_folder):
        os.makedirs(plagiarism_folder)

    # read task config
    task_file = os.path.join(exercise_folder, 'tasks.json')
    with open(task_file) as tasksFH:
        tasks = json.load(tasksFH)
    for task in tasks:
        # Autograded task?
        if not task['manually']:
            # Perform evaluation
            files = task['plagiarism_base_files']

    # flattening files
    dirs = [f for f in os.listdir(output) if os.path.isdir(os.path.join(output, f))]

    for dirc in dirs:
        print(dirc)
        for f in files:
            t_file = os.path.join(os.path.join(output, dirc), f)
            print(t_file)
            print(os.path.isfile(t_file))
            if os.path.isfile(t_file):
                print(os.path.join(plagiarism_folder, dirc + "_" + f))
                shutil.copy(t_file, os.path.join(plagiarism_folder, dirc + "_" + f))

    userid = 78754375

    m = mosspy.Moss(userid, "python")

    for base_file in files:
        m.addBaseFile(os.path.abspath(os.path.join(plagiarism_base_folder, base_file)))

    flaten_dirs = [f for f in os.listdir(plagiarism_folder)]
    for fd in flaten_dirs:
        # print(os.path.abspath(os.path.join(plagiarism_folder, fd)))
        if os.path.isfile(os.path.abspath(os.path.join(plagiarism_folder, fd))):
            m.addFile(os.path.abspath(os.path.join(plagiarism_folder, fd)))

    url = m.send()  # Submission Report URL

    print ("Report Url: " + url)

    # Save report file
    m.saveWebPage(url, plagiarism_folder + "/report.html")

    # Download whole report locally including code diff links
    mosspy.download_report(url, plagiarism_folder + "/report/", connections=8)

    HtmlFile = open(plagiarism_folder + "/report/index.html", encoding='utf-8')
    source_code = HtmlFile.read()

    soup = BeautifulSoup(source_code, "lxml")

    data = []
    table = soup.find('table')

    headers = ["group file 1", "group file 1 similarity","report_file", "group file 2", "group file 2 similarity"]
    print(headers)

    rows = table.select("tr + tr")
    total_temp = []
    for row in rows:
        tds = row.find_all("td")
        print("===========================")
        temp = []
        for td in tds:
            str_text = str(td.text)
            str_pos = str_text.find('Gruppe')
            if str_pos > 0:
                str_text = str_text[str_pos:]
                str_group_name = str_text[:str_text.find(' ')]
                str_group_percent = str_text[str_text.find('(') + 1:str_text.find(')') - 1]
                temp.append(str_group_name)
                temp.append(str_group_percent)
            for r in re.findall(r'(?<=<a href=")[^"]*', str(td.a)):
                if str(r) not in temp:
                    temp.append(str(r))
            if (len(temp) == 5):
                print(temp)
                if int(temp[1])>threshold or int(temp[4])>threshold:
                    total_temp.append(temp)
                    break

    with open(plagiarism_folder+"/out.csv", "a") as f:
        wr = csv.writer(f)
        wr.writerow(headers)
        wr.writerows(total_temp)
    return None

if __name__ == '__main__':
    # Command line interface
    parser = argparse.ArgumentParser(description='Checking for plagiarism')

    parser.add_argument('plagiarism_base_folder', metavar='plagiarism_base_folder', type=str, nargs=1,
                        help='plagiarism base folder containing the stencil codes')
    parser.add_argument('output', metavar='output', type=str, nargs='?', default='output',
                        help='output folder containing the exercise extracted files')
    parser.add_argument('exercise_folder', metavar='exercise_folder', type=str, nargs='?',default="exercise",
                        help='exercise folder contain tasks.json')
    parser.add_argument('plagiarism_folder', metavar='plagiarism_folder', type=str, nargs='?',default="plagiarism_output_folder",
                        help='Making plagiarism_output_folder containing output folder of reports')
    parser.add_argument('threshold', metavar='threshold', type=int, nargs='?', default=20,
                        help='Threshold to ignore reports with below percentages of similarity')
    args = parser.parse_args()

    output = args.output[0]
    plagiarism_base_folder = args.plagiarism_base_folder[0]
    exercise_folder = args.exercise_folder[0]
    plagiarism_folder = args.plagiarism_folder[0]
    threshold = args.threshold[0]

    Check(output,plagiarism_base_folder,exercise_folder,plagiarism_folder="plagiarism_output_folder",threshold=20)
