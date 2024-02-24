import webbrowser
from flask import Flask, render_template, request, redirect
import jinja2
import os
import natsort
import socket
from collections import defaultdict
import random
import sys
import json

ROOT_DIR = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__)
app.jinja_env.variable_start_string = '[([('
app.jinja_env.variable_end_string = ')])]'
app.jinja_env.block_start_string = '[([(='
app.jinja_env.block_end_string = '=)])]'
app.jinja_env.comment_start_string = '{#'
app.jinja_env.comment_end_string = '#}'


@app.route('/', methods=['GET', 'POST'])
def index():
    global course_directory

    if request.method == "POST" and request.form.get("folder"):
        for value in request.form.values():
            folder = value
        if folder+".html" in os.listdir(os.path.join(course_directory, folder)):
            load_templates()
            return redirect(f"/{folder}")
        elif folder+".html" not in os.listdir(os.path.join(course_directory, folder)):
            course_directory = os.path.join(course_directory, folder)
            folders = natsort.natsorted(load_folder(course_directory))
            load_toc_if_exist()
            if toc:
                return render_index_with_toc(folder=folder)
            return render_template("index.html", folder_list=folders, folder=folder)
    elif request.method == "POST" and len(root_course_path) < len(course_directory):
        course_directory = os.path.sep.join(
            course_directory.split(os.path.sep)[:-1])
        folders = natsort.natsorted(load_folder(course_directory))
        folder = os.path.split(course_directory)[-1]
        return render_template("index.html", folder_list=folders, folder=folder)
    
    folders = natsort.natsorted(load_folder(course_directory))
    folder = os.path.split(course_directory)[-1]
    load_toc_if_exist()
    if toc:
        return render_index_with_toc(folder=folder)
    return render_template("index.html", folder_list=folders, folder=folder)

def load_toc_if_exist():
    global toc
    toc = None
    if course_directory:
        tocpath = os.path.join(course_directory, "__toc__.json")
        if os.path.exists(tocpath):
            with open(tocpath) as tocfile:
                toc = json.load(tocfile)

def build_toc_render_items():
    toc_items = []
    for item in toc["toc"]:
        if type(item) is dict: # category
            toc_items.append({"title": item["category"], "is_category": True})
            for topic in item["topics"]:
                toc_items.append({"title": topic[1], "is_category": False})
        else: # assessments, projects, cloud labs..
            toc_items.append({"title": item[1], "is_category": False})
    return toc_items

def render_index_with_toc(folder: str):
    toc_items = build_toc_render_items()

    return render_template("index_toc.html", toc_items=toc_items, folder=folder)

def get_ip():
    port = random.randint(1000, 9999)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    while s.connect_ex((ip_address, port)) != 0:
        port = random.randint(1000, 9999)
    s.close()
    return ip_address, port


def check_code_present(topic):
    if len(os.listdir(os.path.join(course_directory, topic))) > 1:
        return True
    return False


def load_topics(course_directory):
    folders_paths = []
    for folders in os.listdir(course_directory):
        folder_path = os.path.join(course_directory, folders)
        if os.path.isdir(folder_path) and os.path.isfile(os.path.join(folder_path, folders+".html")):
            folders_paths.append(folders)
    return folders_paths


def load_folder(course_directory):
    folders_paths = []
    for folders in os.listdir(course_directory):
        folder_path = os.path.join(course_directory, folders)
        if os.path.isdir(folder_path):
            folders_paths.append(folders)
    return folders_paths


def load_files(topic_directory):
    file_contents, file_names, h_map = [], [], defaultdict(str)
    for root, _, files in os.walk(os.path.join(course_directory, topic_directory)):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path) and topic_directory not in file and ".DS_Store" not in file_path:
                content = "\n"
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        f = f.readlines()
                    for line in f:
                        content += f'''{line}'''
                except Exception:
                    pass
                h_map[file_path] = content
    file_path_keys = natsort.natsorted(list(h_map.keys()))
    for file_path in file_path_keys:
        file_contents.append(h_map[file_path])
        file_names.append(
            file_path[len(os.path.join(course_directory, topic_directory)):])
    file_names.append(os.path.join(os.path.split(
        course_directory)[-1], topic_directory))
    return file_contents, file_names

def topics_toc(topics):
    global itr
    toc_items = build_toc_render_items()
    try:
        itr = next(i for i, toc_item in enumerate(toc_items) if toc_item['title'] == topics)
    except StopIteration:
        pass
    if request.method == "POST" and "back" in request.form and itr > 0:
        itr -= 1
    elif request.method == "POST" and "next" in request.form and itr < len(toc_items)-1:
        itr += 1
    elif request.method == 'POST' and "sidebar-topic" in request.form:
        itr = int(request.form.get('sidebar-topic'))
    elif request.method == 'POST' and "home" in request.form:
        itr = 0
        return redirect("/")
    elif request.method == 'POST' and request.form.get("code_filesystem"):
        path = f"file:///{course_directory}/{toc_items[itr]['title']}".replace(
            "\\", "/")
        webbrowser.open(path)
    webpage = f"{toc_items[itr]['title']}/{toc_items[itr]['title']}.html"
    is_code_present = check_code_present(
        toc_items[itr]['title'])
    rendered_html = render_template(
        "topics_toc.html", code_present=is_code_present, webpage=webpage, folder=f"{toc_items[itr]['title']}", toc_items=toc_items, itr=itr)
    return rendered_html

@app.route("/<topics>", methods=['GET', 'POST'])
def topics(topics):
    global itr
    if toc:
        return topics_toc(topics)
    topic_folders = natsort.natsorted(load_topics(course_directory))
    try:
        itr = int(topic_folders.index(topics))
    except ValueError:
        pass
    if request.method == "POST" and "back" in request.form and itr > 0:
        itr -= 1
    elif request.method == "POST" and "next" in request.form and itr < len(topic_folders)-1:
        itr += 1
    elif request.method == 'POST' and "sidebar-topic" in request.form:
        itr = int(request.form.get('sidebar-topic'))
    elif request.method == 'POST' and "home" in request.form:
        itr = 0
        return redirect("/")
    elif request.method == 'POST' and request.form.get("code_filesystem"):
        path = f"file:///{course_directory}/{topic_folders[itr]}".replace(
            "\\", "/")
        webbrowser.open(path)
    webpage = f"{topic_folders[itr]}/{topic_folders[itr]}.html"
    is_code_present = check_code_present(
        topic_folders[itr])
    rendered_html = render_template(
        "topics.html", code_present=is_code_present, webpage=webpage, folder=f"{topic_folders[itr]}", folder_list=topic_folders, itr=itr)
    return rendered_html


@app.route("/code/<codes>", methods=['GET', 'POST'])
def codes(codes):
    file_contents, file_names = load_files(codes)
    return render_template("codes.html", file_contents=file_contents, file_names=file_names)


def clear():
    current_os = sys.platform
    if current_os.startswith('darwin'):
        os.system('clear')
    elif current_os.startswith('linux'):
        os.system('clear')
    elif current_os.startswith('win32') or current_os.startswith('cygwin'):
        os.system('cls')


def load_templates():
    my_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader([f'{ROOT_DIR}/templates',
                                 f'{course_directory}']),
    ])
    app.jinja_loader = my_loader


def initialization():
    clear()
    print(f'''
                            Educative Viewer, made by Anilabha Datta
                            Project Link: https://github.com/anilabhadatta/educative-viewer
                            Read the documentation for more information about this project.
                            
                            -> For Cloudflare Tunneling, enter the following command in a new terminal
                                    For random cloudflare tunnel url : cloudflared tunnel -url {ip_address}:{port}
                                    For custom domain tunnel url : 
                                                        Step 1: Modify Ip:Port in config.yml
                                                        Step 2: Enter "cloudflared tunnel run" in terminal
                            -> Leave Blank and press Enter to exit
            ''')


if __name__ == "__main__":
    ip_address, port = get_ip()
    initialization()
    try:
        while True:
            initialization()
            course_directory = input("Enter Course Directory Path: ")
            if course_directory == '':
                break
            elif os.path.isdir(course_directory):
                itr = 0
                root_course_path = course_directory
                load_templates()
                print(
                    f'''

                    To Open Mobile/Desktop View,
                    Tunnel Url: Use the url from cloudflare terminal window or the custom domain url
                    Localhost Url: http://{ip_address}:{port}
                    
                    ''')
                app.run(host="0.0.0.0", threaded=True, port=port, debug=False)
            else:
                print("Invalid path")
                input("Press enter to continue")
    except KeyboardInterrupt:
        print("Exited")
    except Exception as e:
        print("Exited", e)
