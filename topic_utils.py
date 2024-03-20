# import json
# import os
# from collections import defaultdict
# import webbrowser
# from flask import redirect, render_template, request
# import natsort


# def load_files(topic_dir, course_dir):
#     file_contents, file_names, h_map = [], [], defaultdict(str)
#     for root, _, files in os.walk(os.path.join(course_dir, topic_dir)):
#         for file in files:
#             file_path = os.path.join(root, file)
#             if os.path.isfile(file_path) and topic_dir not in file and ".DS_Store" not in file_path:
#                 content = "\n"
#                 try:
#                     with open(file_path, 'r', encoding='utf-8') as f:
#                         f = f.readlines()
#                     for line in f:
#                         content += f'''{line}'''
#                 except Exception:
#                     pass
#                 h_map[file_path] = content
#     file_path_keys = natsort.natsorted(list(h_map.keys()))
#     for file_path in file_path_keys:
#         file_contents.append(h_map[file_path])
#         file_names.append(
#             file_path[len(os.path.join(course_dir, topic_dir)):])
#     file_names.append(os.path.join(os.path.split(
#         course_dir)[-1], topic_dir))
#     return file_contents, file_names





# def check_code_present(topic, course_dir):
#     if len(os.listdir(os.path.join(course_dir, topic))) > 1:
#         return True
#     return False


# def load_topics(course_dir):
#     folders_paths = []
#     for folder in os.listdir(course_dir):
#         folder_path = os.path.join(course_dir, folder)
#         if os.path.isdir(folder_path) and os.path.isfile(os.path.join(folder_path, folder+".html")):
#             folders_paths.append(folder)
#     return folders_paths








# def topics_toc(topics):
#     global itr
#     toc_items = build_toc_render_items()
#     try:
#         itr = next(i for i, toc_item in enumerate(toc_items) if toc_item['title'] == topics)
#     except StopIteration:
#         pass
#     print(f"Old Itr: {itr}")
#     if request.method == "POST" and "back" in request.form and itr > 0:
#         if toc_items[itr-1]['is_category']:
#             if itr-1 != 0:
#                 itr -= 1
#             else:
#                 itr += 1
#         itr -= 1
#     elif request.method == "POST" and "next" in request.form and itr < len(toc_items)-1:
#         if toc_items[itr+1]['is_category']:
#             if itr+1 != len(toc_items)-1:
#                 itr += 1
#             else:
#                 itr -= 1
#         itr += 1
#     elif request.method == 'POST' and "sidebar-topic" in request.form:
#         itr = int(request.form.get('sidebar-topic'))
#     elif request.method == 'POST' and "home" in request.form:
#         itr = 0
#         return redirect("/")
#     elif request.method == 'POST' and request.form.get("code_filesystem"):
#         path = f"file:///{course_directory}/{toc_items[itr]['title']}".replace(
#             "\\", "/")
#         webbrowser.open(path)
#     webpage = f"{toc_items[itr]['title']}/{toc_items[itr]['title']}.html"
#     print(f"New Itr: {itr} Webpage {webpage}")
#     is_code_present = check_code_present(
#         toc_items[itr]['title'])
#     with open(os.path.join(course_directory, webpage), 'r', encoding='utf-8') as file:
#         htmlData = file.read()
#     rendered_html = render_template(
#         "topics_toc.html", code_present=is_code_present, webpage=webpage, folder=f"{toc_items[itr]['title']}", toc_items=toc_items, itr=itr, htmlData=htmlData)
#     return rendered_html

