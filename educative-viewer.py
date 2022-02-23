from distutils.log import debug
import webbrowser
from flask import Flask, render_template, request, redirect
import jinja2
import os
import natsort

ROOT_DIR = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    topic_folders = natsort.natsorted(load_folder(course_directory))
    if request.method == "POST":
        for key in request.form.keys():
            topic = key
        return redirect(f"/{topic}")
    return render_template("index.html", topic_list=topic_folders)


def check_code_present(topic):
    if len(os.listdir(os.path.join(course_directory, topic))) > 1:
        return True
    return False


def load_folder(course_directory):
    folders = [os.path.join(course_directory, f)
               for f in os.listdir(course_directory)]
    res = []
    for folder in folders:
        if os.path.isdir(folder):
            res.append(os.path.split(folder)[-1])
    return res


def load_files(topic_directory):
    file_contents, file_names = [], []
    for root, _, files in os.walk(os.path.join(course_directory, topic_directory)):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path) and topic_directory not in file:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f = f.readlines()
                content = "\n"
                for line in f:
                    content += f'''{line}'''
                file_contents.append(content)
                file_names.append(file_path)
    return file_contents, file_names


@app.route("/<topics>", methods=['GET', 'POST'])
def topics(topics):
    global itr
    topic_folders = natsort.natsorted(load_folder(course_directory))
    try:
        itr = int(topic_folders.index(topics))
    except ValueError:
        pass
    if request.method == "POST" and request.form.get("back") and itr > 0:
        itr -= 1
        return render_template("topics.html", code_present=check_code_present(topic_folders[itr]), webpage=f"{topic_folders[itr]}/{topic_folders[itr]}.html",  folder=f"{topic_folders[itr]}")
    elif request.method == "POST" and request.form.get("forward") and itr < len(topic_folders)-1:
        itr += 1
        return render_template("topics.html", code_present=check_code_present(topic_folders[itr]), webpage=f"{topic_folders[itr]}/{topic_folders[itr]}.html", folder=f"{topic_folders[itr]}")
    elif request.method == 'POST' and request.form.get("home"):
        itr = 0
        return redirect("/")
    elif request.method == 'POST' and request.form.get("code_filesystem"):
        path = f"file:///{course_directory}/{topic_folders[itr]}"
        path = path.replace("\\", "/")
        webbrowser.open(path)
    return render_template("topics.html", code_present=check_code_present(topic_folders[itr]), webpage=f"{topic_folders[itr]}/{topic_folders[itr]}.html", folder=f"{topic_folders[itr]}")


@app.route("/code/<codes>", methods=['GET', 'POST'])
def codes(codes):
    file_contents, file_names = load_files(codes)
    return render_template("codes.html", file_contents=file_contents, file_names=file_names)


def clear():
    if os.name == "nt":
        os.system('cls')
    else:
        os.system('clear')


if __name__ == "__main__":

    while True:
        clear()
        print('''
                        Educative viewer, made by Anilabha Datta
                        Project Link: https://github.com/anilabhadatta/educative-viewer
                        Read the documentation for more information about this project.

                        -> Enter Course path to start the server
                        -> Leave Blank and press Enter to exit
        ''')
        course_directory = input("User Input: ")
        if course_directory == '':
            break
        elif os.path.isdir(course_directory):
            itr = 0
            my_loader = jinja2.ChoiceLoader([
                app.jinja_loader,
                jinja2.FileSystemLoader([f'{ROOT_DIR}/templates',
                                         f'{course_directory}']),
            ])
            app.jinja_loader = my_loader
            app.run(host="0.0.0.0", threaded=True)
        else:
            print("Invalid path")
            input("Press enter to continue")
