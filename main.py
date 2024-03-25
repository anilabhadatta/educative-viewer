import base64
import glob
import json
import webbrowser
from flask import Blueprint, jsonify, render_template, request, redirect, send_file, session, url_for, flash
from flask_login import login_required, current_user
import natsort

from .topic_utils import check_code_present, load_files, load_topics

from .models import UserDetails

from . import db
import os

main = Blueprint('main', __name__)
root_course_dir = os.getenv('course_dir', '.')

@main.route('/edu-viewer/')
def index():
    return render_template('index.html')


@main.route('/edu-viewer/favicon.ico')
def favicon():
    return url_for('static', filename='images/favicon.ico')


@main.route('/edu-viewer/courses', methods=['GET', 'POST'])
@login_required
def courses():
    highlight_idx = None
    last_visited_topic = ""
    current_user_details = UserDetails.query.filter_by(
            username=current_user.username).first()
    if current_user_details is None:
        course_dir = root_course_dir
    else:
        course_dir = current_user_details.last_visited_course
        last_visited_topic = current_user_details.last_visited_topic
    if request.method == "POST" and request.form.get("folder"):
        folder = request.form.get("folder")
        course_dir = os.path.join(course_dir, folder)
        if folder+".html" not in os.listdir(course_dir):
            current_user_details = UserDetails(
                username=current_user.username, last_visited_course=course_dir, last_visited_topic=last_visited_topic, last_visited_index=0)
            db.session.merge(current_user_details)
            db.session.commit()
            
        if folder+".html" in os.listdir(course_dir):
            # load_templates()
            return redirect(f"/edu-viewer/courses/{folder}")
        elif folder+".html" not in os.listdir(course_dir):
            folders = natsort.natsorted(load_folder(course_dir))
            if last_visited_topic in folders:
                highlight_idx = folders.index(last_visited_topic)
            toc = load_toc_if_exist(course_dir)
            if toc:
                return render_index_with_toc(folder, toc, highlight_idx)
            return render_template("courses.html", folder_list=folders, folder=folder, highlight_idx=highlight_idx)
    elif request.method == "POST":
        current_user_details = UserDetails.query.filter_by(
            username=current_user.username).first()
        course_dir = current_user_details.last_visited_course
        if len(root_course_dir) < len(course_dir):
            course_dir = os.path.sep.join(
                course_dir.split(os.path.sep)[:-1])
            current_user_details = UserDetails(
            username=current_user.username, last_visited_course=course_dir, last_visited_topic=last_visited_topic, last_visited_index=0)
            db.session.merge(current_user_details)
            db.session.commit()
            folders = natsort.natsorted(load_folder(course_dir))
            folder = os.path.split(course_dir)[-1]
            if last_visited_topic in folders:
                highlight_idx = folders.index(last_visited_topic)
            return render_template("courses.html", folder_list=folders, folder=folder, highlight_idx=highlight_idx)
    current_user_details = UserDetails.query.filter_by(
            username=current_user.username).first()
    if current_user_details is None:
        course_dir = root_course_dir
    else:
        course_dir = current_user_details.last_visited_course
    folders = natsort.natsorted(load_folder(course_dir))
    folder = os.path.split(course_dir)[-1]
    if last_visited_topic in folders:
        highlight_idx = folders.index(last_visited_topic)
    toc = load_toc_if_exist(course_dir)
    if toc:
        return render_index_with_toc(folder, toc, highlight_idx)
    return render_template("courses.html", folder_list=folders, folder=folder, highlight_idx=highlight_idx)

def load_folder(course_dir):
    folders_paths = []
    for folder in os.listdir(course_dir):
        folder_path = os.path.join(course_dir, folder)
        if os.path.isdir(folder_path):
            folders_paths.append(folder)
    return folders_paths

def load_toc_if_exist(course_dir):
    toc = None
    if course_dir:
        tocpath = os.path.join(course_dir, "__toc__.json")
        if os.path.exists(tocpath):
            with open(tocpath) as tocfile:
                toc = json.load(tocfile)
    return toc

def render_index_with_toc(folder, toc, highlight_idx):
    toc_items = build_toc_render_items(toc, highlight_idx)
    return render_template("courses_toc.html", toc_items=toc_items, folder=folder)

def build_toc_render_items(toc, highlight_idx=0):
    toc_items = []
    curr_topic_idx = 0
    for item in toc["toc"]:
        if type(item) is dict: # category
            toc_items.append({"title": item["category"], "is_category": True, "color": "white"})
            for topic in item["topics"]:
                toc_items.append({"title": topic[1], "is_category": False, "color": "white" if curr_topic_idx != highlight_idx else "#0dfd10"})
                curr_topic_idx += 1
        else: # assessments, projects, cloud labs..
            toc_items.append({"title": item[1], "is_category": False, "color": "white" if curr_topic_idx != highlight_idx else "#0dfd10"})
            curr_topic_idx += 1
    return toc_items



@main.route("/edu-viewer/courses/<topics>", methods=['GET', 'POST'])
@login_required
def topics(topics):
    current_user_details = UserDetails.query.filter_by(
            username=current_user.username).first()
    course_dir = current_user_details.last_visited_course
    if topics in os.listdir(course_dir):
        topic_index = int(topics.split("-")[0])
        current_user_details = UserDetails(
            username=current_user.username, last_visited_course=course_dir, last_visited_topic=topics, last_visited_index=topic_index)
        db.session.merge(current_user_details)
        db.session.commit()
    else:
        topic_index = current_user_details.last_visited_index
    itr = topic_index
    toc = load_toc_if_exist(course_dir)
    if toc:
        return topics_toc(topics, course_dir, toc, itr)
    topic_folders = natsort.natsorted(load_topics(course_dir))
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
        return redirect("/edu-viewer/courses")
    elif request.method == 'POST' and request.form.get("code_filesystem"):
        path = f"file:///{course_dir}/{topic_folders[itr]}".replace(
            "\\", "/")
        webbrowser.open(path)
    current_user_details = UserDetails(
            username=current_user.username, last_visited_course=course_dir, last_visited_topic=topics, last_visited_index=itr)
    db.session.merge(current_user_details)
    db.session.commit()
    template_folder = "/".join(course_dir[len(root_course_dir)+1:].split(os.path.sep))
    webpage = f"{template_folder}/{topic_folders[itr]}/{topic_folders[itr]}.html"
    is_code_present = check_code_present(course_dir, topic_folders[itr])
    rendered_html = render_template(
        "topics.html", code_present=is_code_present, webpage=webpage, folder=f"{topic_folders[itr]}", folder_list=topic_folders, itr=itr)
    return rendered_html

def topics_toc(topics, course_dir, toc, itr):
    toc_items = build_toc_render_items(toc)
    try:
        itr = next(i for i, toc_item in enumerate(toc_items) if toc_item['title'] == topics)
    except StopIteration:
        pass
    if request.method == "POST" and "back" in request.form and itr > 0:
        if toc_items[itr-1]['is_category']:
            if itr-1 != 0:
                itr -= 1
            else:
                itr += 1
        itr -= 1
    elif request.method == "POST" and "next" in request.form and itr < len(toc_items)-1:
        if toc_items[itr+1]['is_category']:
            if itr+1 != len(toc_items)-1:
                itr += 1
            else:
                itr -= 1
        itr += 1
    elif request.method == 'POST' and "sidebar-topic" in request.form:
        itr = int(request.form.get('sidebar-topic'))
    elif request.method == 'POST' and "home" in request.form:
        itr = 0
        return redirect("/edu-viewer/courses")
    elif request.method == 'POST' and request.form.get("code_filesystem"):
        path = f"file:///{course_dir}/{toc_items[itr]['title']}".replace(
            "\\", "/")
        webbrowser.open(path)
    current_user_details = UserDetails(
            username=current_user.username, last_visited_course=course_dir, last_visited_topic=topics, last_visited_index=itr)
    db.session.merge(current_user_details)
    db.session.commit()
    template_folder = "/".join(course_dir[len(root_course_dir)+1:].split(os.path.sep))
    webpage = f"{template_folder}/{toc_items[itr]['title']}/{toc_items[itr]['title']}.html"
    is_code_present = check_code_present(course_dir, toc_items[itr]['title'])
    rendered_html = render_template(
        "topics_toc.html", code_present=is_code_present, webpage=webpage, folder=f"{toc_items[itr]['title']}", toc_items=toc_items, itr=itr)
    return rendered_html

@main.route("/edu-viewer/courses/code/<codes>", methods=['GET', 'POST'])
@login_required
def codes(codes):
    current_user_details = UserDetails.query.filter_by(
            username=current_user.username).first()
    course_dir = current_user_details.last_visited_course
    directory_path = os.path.join(course_dir, codes)
    encoded_path = base64.b64encode(directory_path.encode()).decode()
    return render_template("monaco-editor.html", encoded_path=encoded_path)


def build_folder_structure(directory, root):
    structure = []

    for item in glob.glob(os.path.join(directory, '*')):
        if os.path.isdir(item):
            folder_name = os.path.basename(item)
            node = {"text": folder_name, "nodes": []}

            # Recursively build structure for subfolder
            substructure = build_folder_structure(item, root)
            if substructure:
                node["nodes"].extend(substructure)

            structure.append(node)
        elif os.path.isfile(item):
            filename = os.path.basename(item)
            if filename != f"{os.path.splitext(filename)[0]}.html":
                file_path = os.path.join(directory, filename)
                file_path = os.path.relpath(file_path, root)
                encoded_path = base64.b64encode(file_path.encode()).decode()
                structure.append({"text": filename, "type": "file", "encoded_path": encoded_path})

    return structure

# Endpoint to list files in a directory
@main.route('/edu-viewer/courses/list-files')
@login_required
def list_files():
    encoded_path = request.args.get('encoded_path')
    directory_path = base64.b64decode(encoded_path.encode()).decode()
    files = build_folder_structure(directory_path, directory_path)
    return jsonify(files)

# Endpoint to get file content
@main.route('/edu-viewer/courses/file-content/<path:filename>')
@login_required
def file_content(filename):
    encoded_path = request.args.get('encoded_path')
    directory_path = base64.b64decode(encoded_path.encode()).decode()
    filename =  base64.b64decode(filename.encode()).decode()
    file_path = os.path.join(directory_path, filename)
    return send_file(file_path)

@main.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
