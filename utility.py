import base64
import glob
import json
import os


def check_code_present(course_dir, topic):
    if len(os.listdir(os.path.join(course_dir, topic))) > 1:
        return True
    return False


def load_topics(course_dir):
    folders_paths = []
    for folder in os.listdir(course_dir):
        folder_path = os.path.join(course_dir, folder)
        if os.path.isdir(folder_path) and os.path.isfile(os.path.join(folder_path, folder + ".html")):
            folders_paths.append(folder)
    return folders_paths


def load_toc_if_exist(course_dir):
    toc = None
    if course_dir:
        toc_path = os.path.join(course_dir, "__toc__.json")
        if os.path.exists(toc_path):
            with open(toc_path) as toc_file:
                toc = json.load(toc_file)
    return toc


def load_folder(course_dir):
    folders = []
    for folder in os.listdir(course_dir):
        folder_path = os.path.join(course_dir, folder)
        if os.path.isdir(folder_path):
            folders.append(folder)
    return folders


def build_toc_render_items(toc, highlight_idx=0):
    toc_items = []
    curr_topic_idx = 0
    for item in toc["toc"]:
        if type(item) is dict:  # category
            toc_items.append({"title": item["category"], "is_category": True, "color": "white"})
            for topic in item["topics"]:
                toc_items.append({"title": topic[1], "is_category": False,
                                  "color": "white" if curr_topic_idx != highlight_idx else "#0dfd10"})
                curr_topic_idx += 1
        else:  # assessments, projects, cloud labs..
            toc_items.append({"title": item[1], "is_category": False,
                              "color": "white" if curr_topic_idx != highlight_idx else "#0dfd10"})
            curr_topic_idx += 1
    return toc_items


def build_folder_structure_for_monaco_sidebar(directory, root):
    structure = []

    for item in glob.glob(os.path.join(directory, '*')):
        if os.path.isdir(item):
            folder_name = os.path.basename(item)
            node = {"text": folder_name, "nodes": []}

            # Recursively build structure for subfolder
            substructure = build_folder_structure_for_monaco_sidebar(item, root)
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
