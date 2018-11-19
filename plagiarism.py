import os, sys, json
import shutil
import mosspy
from bs4 import BeautifulSoup
import re, csv
import logging
import argparse


MOSSPY_USERID = 78754375


def get_extensions(lang):
    lang_extensions = {
        'java': ['.java'],
        'python': ['.py']
    }
    return lang_extensions[lang]


def get_base_files(base_folder, extensions):
    files = []

    # task_file = os.path.join(exercise_folder, 'tasks.json')
    # with open(task_file) as f:
    #     tasks = json.load(f)
    #
    # for task in tasks:
    #     if 'plagiarism_base_files' in task:
    #         base_files = [os.path.join(exercise_folder, f) for f in task['plagiarism_base_files']]
    #         files.extend(base_files)

    for file in os.listdir(base_folder):
        if os.path.splitext(file)[1] in extensions:
            files.append(os.path.join(base_folder, file))

    return files


def get_files(base_files, output_folder):
    base_files = [os.path.basename(f) for f in base_files]

    files = []

    for group_folder in os.listdir(output_folder):
        if not os.path.isdir(os.path.join(output_folder, group_folder)):
            continue

        if group_folder in ['plagiarism']:  #ignore when scanning for files
            continue

        for filename in base_files:
            file = os.path.join(output_folder, group_folder, filename)
            if os.path.exists(file):
                files.append(file)

    return files

def run_mosspy(base_files, output_folder, ignore_limit):
    plagiarism_output_folder = os.path.join(output_folder, 'plagiarism')
    if not os.path.exists(plagiarism_output_folder):
        os.makedirs(plagiarism_output_folder)

    reports = []
    # Run for each file separately --> better accuracy
    for file in base_files:
        filename = os.path.basename(file)
        m = mosspy.Moss(MOSSPY_USERID, 'java')
        m.setIgnoreLimit(int(ignore_limit))

        m.addBaseFile(file)

        for f in get_files([file], output_folder):
            m.addFile(f)

        report_url = m.send()  # Submission Report URL

        if report_url.startswith('Error:'):
            print(f"Error for {filename}: {report_url}")
            continue
        else:
            print(f"Report Url for {filename}: {report_url}")


        print(f"Downloading reports for {filename}... ", end='')
        # report_file = os.path.join(output_folder, 'report.html')
        # m.saveWebPage(report_url, report_file)

        report_folder = os.path.join(plagiarism_output_folder, f"reports_{filename}/")
        mosspy.download_report(report_url, report_folder, connections=8, log_level=logging.WARNING)
        print('Done')

        reports.append({
            'file': filename,
            'report': report_folder
        })

    return reports


def write_graph(filename, names, data):
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    nodes = []
    node_to_id = {}
    edges = []
    legend = []

    def get_group_from_file(file):
        return os.path.basename(os.path.dirname(file))


    def get_nodes():
        groups = set()
        for d in data:
            groups.add(get_group_from_file(d['file1']))
            groups.add(get_group_from_file(d['file2']))

        for i, g in enumerate(groups):
            nodes.append({
                'id': i,
                'label': g
            })
            node_to_id[g] = i

        return nodes


    def get_edges():
        def get_url(f):
            return os.path.join(os.path.basename(os.path.dirname(f)), os.path.basename(f))

        for d in data:
            src = get_group_from_file(d['file1'])
            dest = get_group_from_file(d['file2'])
            file = os.path.basename(d['file1'])
            edges.append({
                'from': node_to_id[src],
                'to': node_to_id[dest],
                'value': d['percent1'] + d['percent2'],
                'url': get_url(d['html_file']),
                'color': {
                    'color': colors[names.index(file)]
                },
                'title': f"{d['percent1']}% > {file} < {d['percent2']}%"
            })

    def get_legend():
        for i, label in enumerate(names):
            legend.append({
                'id': -(i+1),
                'color': {
                    'background': colors[i]
                },
                'fixed': True,
                'physics': False,
                'label': label,
                'font': {
                    'size': 18
                },
                'size': 25,
                'shape': 'square'
            })


    get_nodes()
    get_edges()
    get_legend()

    html = f"""
<!doctype html>
<html>
<head>
  <title>Plagiarism Graph</title>

  <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
  <link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet" type="text/css" />
  <style type="text/css">
    html, body {{
      height: 100%;
      margin: 0;
    }}
    #mynetwork {{
      width: 100%;
      height: 100%;
    }}
  </style>
</head>
<body>
<div id="mynetwork"></div>
<script type="text/javascript">
  // create an array with nodes
  var nodes = new vis.DataSet({json.dumps(nodes)});

  // create an array with edges
  var edges = new vis.DataSet({json.dumps(edges)});

  // create a network
  var container = document.getElementById('mynetwork');

  var x = -mynetwork.clientWidth;
  var y = -mynetwork.clientHeight;
  var step = 100;
  nodes.add({json.dumps(legend)}.map((node, i) => {{
    node.x = x;
    node.y = y + i*step;
    return node;
  }}));

  var data = {{
    nodes: nodes,
    edges: edges
  }};
  var options = {{
    "physics": {{
        "forceAtlas2Based": {{
          "springLength": 100,
          "avoidOverlap": 1
        }},
        "minVelocity": 0.75,
        "solver": "forceAtlas2Based"
    }}
    //configure: {{
    //    enabled: true,
    //    showButton: true
    //}}
  }};
  var network = new vis.Network(container, data, options);
  network.on("click", function(params) {{
    if (params.edges.length == 1) {{
        var edgeId = params.edges[0];
        if (edges.get(edgeId).url != null) {{
            window.open(edges.get(edgeId).url, '_blank');
        }}
    }}
  }});
</script>
</body>
</html>
    """

    with open(filename, 'w') as f:
        f.write(html)

    print(f"{filename} written.")

def parse_reports(output_folder, reports, limit):
    data = []
    graph_data = []
    names = []

    for r in reports:
        name, report_folder = r['file'], r['report']
        names.append(name)
        # print(name, report_folder)

        report_file = os.path.join(report_folder, 'index.html')
        html = None
        with open(report_file, 'r') as f:
            html = f.read()

        soup = BeautifulSoup(html, 'lxml')
        table = soup.find('table')

        for i, row in enumerate(table.find_all('tr')[1:]):
            tds = row.find_all('td')
            # <tr>
            #     <td><a href="match0.html">ex2/output/Group_18/HeapTable.java (46%)</a></td>
            #     <td><a href="match0.html">ex2/output/Group_37/HeapTable.java (59%)</a></td>
            #     <td align="right">35</td>
            # </tr>
            item = {
                'html_file': os.path.join(report_folder, tds[0].find('a')['href']),
                'file1': re.match(r'(.+)\s\((\d+)%\)', tds[0].get_text())[1],
                'percent1': int(re.match(r'(.+)\s\((\d+)%\)', tds[0].get_text())[2]),
                'file2': re.match(r'(.+)\s\((\d+)%\)', tds[1].get_text())[1],
                'percent2': int(re.match(r'(.+)\s\((\d+)%\)', tds[1].get_text())[2]),
                'lines': int(tds[2].get_text())
            }

            data.append(item)
            if i < limit:
                graph_data.append(item)

    write_graph(os.path.join(output_folder, 'plagiarism', 'graph.html'), names, graph_data)

    data = sorted(data, key=lambda x: x['percent1']+x['percent2'], reverse=True)

    keys = ['file1', 'percent1', 'file2', 'percent2', 'lines', 'html_file'] #data[0].keys()
    with open(os.path.join(output_folder, 'plagiarism', 'results.csv'), 'w') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        def get_filename(file):
            folder = os.path.basename(os.path.dirname(file))
            return os.path.join(folder, os.path.basename(file))

        for item in data:
            item['file1'] = get_filename(item['file1'])
            item['file2'] = get_filename(item['file2'])
            item['html_file'] = get_filename(item['html_file'])
            dict_writer.writerow(item)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Checking for plagiarism')

    parser.add_argument('base', metavar='base', type=str, nargs=1,
                        help='Basefiles are stencil files without implementation of the exercises')
    parser.add_argument('submissions', metavar='submissions', type=str, nargs=1,
                        help='folder containing the submissions')
    parser.add_argument('output', metavar='output', type=str, nargs=1,
                        help='output folder (will contain grade table, unziped files, test run results, ...')

    parser.add_argument('--threshold', metavar='threshold', type=int, default=10,
                        help='Ignore-level to ignore reports with below percentages of similarity')
    parser.add_argument('--lang', metavar='lang', type=str, default='java',
                        help='Specify programming language')
    parser.add_argument('--limit', metavar='limit', type=int, default=20,
                        help='Limit Edges in generated graph')
    args = parser.parse_args()

    base_folder = args.base[0]
    submission_folder = args.submissions[0]
    output_folder = args.output[0]
    threshold = args.threshold
    lang = args.lang
    limit = args.limit


    reports = run_mosspy(
        base_files = get_base_files(base_folder, get_extensions(lang)),
        output_folder = output_folder,
        ignore_limit = threshold
    )

    #reports = [{'file': 'SQLVarchar.java', 'report': 'ex2/output/plagiarism/reports_SQLVarchar.java/'}, {'file': 'HeapTable.java', 'report': 'ex2/output/plagiarism/reports_HeapTable.java/'}, {'file': 'RowPage.java', 'report': 'ex2/output/plagiarism/reports_RowPage.java/'}, {'file': 'SQLInteger.java', 'report': 'ex2/output/plagiarism/reports_SQLInteger.java/'}]

    parse_reports(output_folder, reports, limit)
