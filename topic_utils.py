# import json
import os
from collections import defaultdict
import webbrowser
from flask import redirect, render_template, request
import natsort


def load_files(topic_dir, course_dir):
    file_contents, file_names, h_map = [], [], defaultdict(str)
    for root, _, files in os.walk(os.path.join(course_dir, topic_dir)):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path) and topic_dir not in file and ".DS_Store" not in file_path:
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
            file_path[len(os.path.join(course_dir, topic_dir)):])
    file_names.append(os.path.join(os.path.split(
        course_dir)[-1], topic_dir))
    return file_contents, file_names


def check_code_present(topic, course_dir):
    if len(os.listdir(os.path.join(course_dir, topic))) > 1:
        return True
    return False


def load_topics(course_dir):
    folders_paths = []
    for folder in os.listdir(course_dir):
        folder_path = os.path.join(course_dir, folder)
        if os.path.isdir(folder_path) and os.path.isfile(os.path.join(folder_path, folder+".html")):
            folders_paths.append(folder)
    return folders_paths