import json
import webbrowser
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import natsort

from .models import UserDetails

from . import db
import os

main = Blueprint('main', __name__)
root_course_dir = os.getenv('course_dir', '.')

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/favicon.ico')
def favicon():
    return url_for('static', filename='images/favicon.ico')


@main.route('/courses', methods=['GET', 'POST'])
@login_required
def courses():
    if request.method == "POST" and request.form.get("folder"):
        folder = request.form.get("folder")
        current_user_details = UserDetails.query.filter_by(
            username=current_user.username).first()
        if current_user_details is None:
            course_dir = root_course_dir
        else:
            course_dir = current_user_details.last_visited_course
        course_dir = os.path.join(course_dir, folder)
        print(course_dir, current_user.username)
        current_user_details = UserDetails(
            username=current_user.username, last_visited_course=course_dir, last_visited_topic="", last_visited_index=0)
        db.session.merge(current_user_details)
        db.session.commit()
        
        if folder+".html" in os.listdir(course_dir):
            # load_templates()
            return redirect(f"/{folder}")
        elif folder+".html" not in os.listdir(course_dir):
            folders = natsort.natsorted(load_folder(course_dir))
            toc = load_toc_if_exist(course_dir)
            if toc:
                return render_index_with_toc(folder, toc)
            return render_template("courses.html", folder_list=folders, folder=folder)
    elif request.method == "POST":
        current_user_details = UserDetails.query.filter_by(
            username=current_user.username).first()
        course_dir = current_user_details.last_visited_course
        if len(root_course_dir) < len(course_dir):
            course_dir = os.path.sep.join(
                course_dir.split(os.path.sep)[:-1])
            current_user_details = UserDetails(
            username=current_user.username, last_visited_course=course_dir, last_visited_topic="", last_visited_index=0)
            db.session.merge(current_user_details)
            db.session.commit()
            folders = natsort.natsorted(load_folder(course_dir))
            folder = os.path.split(course_dir)[-1]
            return render_template("courses.html", folder_list=folders, folder=folder)
    current_user_details = UserDetails.query.filter_by(
            username=current_user.username).first()
    if current_user_details is None:
        course_dir = root_course_dir
    else:
        course_dir = current_user_details.last_visited_course
    folders = natsort.natsorted(load_folder(course_dir))
    folder = os.path.split(course_dir)[-1]
    toc = load_toc_if_exist(course_dir)
    if toc:
        return render_index_with_toc(folder, toc)
    return render_template("courses.html", folder_list=folders, folder=folder)

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

def render_index_with_toc(folder, toc):
    toc_items = build_toc_render_items(toc)
    return render_template("courses_toc.html", toc_items=toc_items, folder=folder)

def build_toc_render_items(toc):
    toc_items = []
    for item in toc["toc"]:
        if type(item) is dict: # category
            toc_items.append({"title": item["category"], "is_category": True})
            for topic in item["topics"]:
                toc_items.append({"title": topic[1], "is_category": False})
        else: # assessments, projects, cloud labs..
            toc_items.append({"title": item[1], "is_category": False})
    return toc_items



# @app.route("/<topics>", methods=['GET', 'POST'])
# def topics(topics):
#     global itr
#     if toc:
#         return topics_toc(topics)
#     topic_folders = natsort.natsorted(load_topics(course_dir))
#     try:
#         itr = int(topic_folders.index(topics))
#     except ValueError:
#         pass
#     if request.method == "POST" and "back" in request.form and itr > 0:
#         itr -= 1
#     elif request.method == "POST" and "next" in request.form and itr < len(topic_folders)-1:
#         itr += 1
#     elif request.method == 'POST' and "sidebar-topic" in request.form:
#         itr = int(request.form.get('sidebar-topic'))
#     elif request.method == 'POST' and "home" in request.form:
#         itr = 0
#         return redirect("/")
#     elif request.method == 'POST' and request.form.get("code_filesystem"):
#         path = f"file:///{course_dir}/{topic_folders[itr]}".replace(
#             "\\", "/")
#         webbrowser.open(path)
#     webpage = f"{topic_folders[itr]}/{topic_folders[itr]}.html"
#     is_code_present = check_code_present(
#         topic_folders[itr])
#     rendered_html = render_template(
#         "topics.html", code_present=is_code_present, webpage=webpage, folder=f"{topic_folders[itr]}", folder_list=topic_folders, itr=itr)
#     return rendered_html


# @app.route("/code/<codes>", methods=['GET', 'POST'])
# def codes(codes):
#     file_contents, file_names = load_files(codes)
#     return render_template("codes.html", file_contents=file_contents, file_names=file_names)



# def find_index(key, keys):
#     for i, k in enumerate(keys):
#         if key in k:
#             return i
#     return -1


# def exp_html_template(i=1, company="", role="", tech_stack="", description="", start_date="", end_date="", disabled="", hidden="", resume=False):
#     return f""" 
#         <div id="exp_box"> 
#             <h1 >&nbsp&nbspExperience {i}</h1>
#                 <div class="control" style="display: flex;">
#                         <div class="control"  style="display: flex;  padding: 0.5rem;">
#                         <input {disabled} class="input is-normal" type="text" name="exp_1_{i}" id="exp_1_{i}" placeholder="Company Title" class="form-control name_list" value="{company}"/>
#                         </div>
#                         <div class="control"  style="display: flex;  padding: 0.5rem;">
#                         <input {disabled} class="input is-normal" type="text" name="exp_2_{i}" id="exp_2_{i}" placeholder="Role" class="form-control name_list" value="{role}"/>
#                         </div>
#                         <div class="control"  style="display: flex;  padding: 0.5rem;">
#                         <input {disabled} class="input is-normal" type="text" name="exp_3_{i}" id="exp_3_{i}" placeholder="Tech Stack" class="form-control name_list" value="{tech_stack}"/>
#                         </div>
#                         <div class="control"  style="display: flex;  padding: 0.5rem;">
#                         <input {disabled} class="input is-normal" type="month" name="exp_5_{i}" id="exp_5_{i}" style="width: 10.5rem;" placeholder="Start Date" class="form-control name_list" value="{start_date}"/>
#                         </div>
#                         <div class="control"  style="display: flex;  padding: 0.5rem;">
#                         <input {disabled} class="input is-normal" type="month" name="exp_6_{i}" id="exp_6_{i}" style="width: 10.5rem;" placeholder="End Date" class="form-control name_list" value="{end_date}"/>
#                         </div>
#                         <a href="#" style="display: flex;  padding: 0.5rem;" class="btn btn-danger removeclass {hidden} is-normal">&nbspRemove</a>\
#                 </div>
#                 <div class="control"  style="display: flex;  padding: 0.5rem;">
#                         <textarea {disabled} name="exp_4_{i}" id="exp_4_{i}" class="textarea is-info" placeholder="About your Experience">{description}</textarea>
#                 </div>
#         </div> 
#     """ if not resume else ""


# def pro_html_template(i=1, project_title="", tech_stack="",
#                       project_link="", description="", start_date="", end_date="", disabled="", hidden="", resume=False):
#     return f"""
#         <div id="pro_box">
#           <h1 >&nbsp&nbspProject {i}</h1>
#             <div class="control" style="display: flex;">
#                     <div class="control"  style="display: flex;  padding: 0.5rem;">
#                       <input {disabled} class="input is-normal" type="text" name="pro_1_{i}" id="pro_1_{i}" placeholder="Project Title" class="form-control name_list" value="{project_title}"/>
#                     </div>
#                     <div class="control"  style="display: flex;  padding: 0.5rem;">
#                       <input {disabled} class="input is-normal" type="text" name="pro_2_{i}" id="pro_2_{i}" placeholder="Tech Stack" class="form-control name_list" value="{tech_stack}"/>
#                     </div>
#                     <div class="control"  style="display: flex;  padding: 0.5rem;">
#                       <input {disabled} class="input is-normal is-link" type="text" name="pro_3_{i}" id="pro_3_{i}" placeholder="Github Link" class="form-control name_list" value="{project_link}"/>
#                     </div>
#                     <div class="control"  style="display: flex;  padding: 0.5rem;">
#                       <input {disabled} class="input is-normal" type="month" name="pro_5_{i}" id="pro_5_{i}" style="width: 10.5rem;" placeholder="Start Date" class="form-control name_list"  value="{start_date}"/>
#                     </div>
#                     <div class="control"  style="display: flex;  padding: 0.5rem;">
#                       <input {disabled} class="input is-normal" type="month" name="pro_6_{i}" id="pro_6_{i}" style="width: 10.5rem;" placeholder="End Date" class="form-control name_list"  value="{end_date}" />
#                     </div>
#                     <a href="#" style="display: flex;  padding: 0.5rem;" class="btn btn-danger removeclass {hidden} is-normal">&nbspRemove</a>
#             </div>
#             <div class="control"  style="display: flex;  padding: 0.5rem;">
#                       <textarea {disabled} name="pro_4_{i}" id="pro_4_{i}" class="textarea is-info" placeholder="About your Project">{description}</textarea>
#             </div>
#           </div>
    
#     """ if not resume else ""


# def reverse_date(date, resume=False):
#     if not resume:
#         return "-".join(date.split('-')[::-1])
#     return date


# def generate_dict(username, disabled="", hidden="", resume=False):
#     basic_details = UserDetails.query.filter_by(
#         username=username).first()
#     college_details = Education.query.filter_by(
#         username=username).first()
#     skills = Skills.query.filter_by(username=username).first()
#     coding = Coding.query.filter_by(username=username).first()
#     achievements = Achievements.query.filter_by(
#         username=username).first()
#     experience = Experience.query.filter_by(
#         username=username).all()
#     projects = Projects.query.filter_by(
#         username=username).all()

#     try:
#         res_html_exp, res_html_pro = "", ""
#         experience_data, projects_data = [], []
#         for i, exp in enumerate(experience, start=1):
#             company = exp.company_title
#             role = exp.role
#             tech_stack = exp.tech_stack
#             description = exp.description
#             start_date = reverse_date(exp.start_date, resume)
#             end_date = reverse_date(exp.end_date, resume)
#             res_html_exp += exp_html_template(i, company, role,
#                                               tech_stack, description, start_date, end_date, disabled=disabled, hidden=hidden, resume=resume)
#             experience_data += [company, role, tech_stack,
#                                 description, start_date, end_date]
#         for i, pro in enumerate(projects, start=1):
#             project_title = pro.project_title
#             tech_stack = pro.tech_stack
#             project_link = pro.project_link
#             description = pro.description
#             start_date = reverse_date(pro.start_date, resume)
#             end_date = reverse_date(pro.end_date, resume)
#             res_html_pro += pro_html_template(i, project_title, tech_stack,
#                                               project_link, description, start_date, end_date, disabled=disabled, hidden=hidden, resume=resume)
#             projects_data += [project_title, tech_stack,
#                               project_link, description, start_date, end_date]
#         dic = {
#             "username": username,
#             "full_name": basic_details.full_name,
#             "phone_number": basic_details.phone_number,
#             "email": basic_details.email,
#             "linkedin": basic_details.linkedin,
#             "github": basic_details.github,
#             "college": college_details.college,
#             "degree": college_details.degree,
#             "college_start": reverse_date(college_details.college_start, resume),
#             "college_end": reverse_date(college_details.college_end, resume),
#             "cgpa": college_details.cgpa,
#             "school": college_details.school,
#             "board": college_details.board,
#             "school_start": reverse_date(college_details.school_start, resume),
#             "school_end": reverse_date(college_details.school_end, resume),
#             "percentage": college_details.percentage,
#             "languages": skills.languages,
#             "frameworks": skills.frameworks,
#             "dev_tools": skills.dev_tools,
#             "codechef": coding.codechef,
#             "codeforces": coding.codeforces,
#             "leetcode": coding.leetcode,
#             "achievements": achievements.achievements,
#             "experience_data": experience_data,
#             "projects_data": projects_data,
#             "res_html_exp": res_html_exp,
#             "res_html_pro": res_html_pro,
#             "x_exp": len(experience),
#             "FieldCount_exp": len(experience),
#             "x_pro": len(projects),
#             "FieldCount_pro": len(projects),
#         }

#     except Exception as e:
#         dic = {
#             "username": username,
#             "res_html_exp": exp_html_template(resume=resume),
#             "res_html_pro": pro_html_template(resume=resume),
#             "x_exp": 1,
#             "FieldCount_exp": 1,
#             "x_pro": 1,
#             "FieldCount_pro": 1,
#         }
#     return dic


# @main.route('/profile', methods=['GET', 'POST'])
# @login_required
# def profile():
#     if request.method == "GET":
#         dic = generate_dict(current_user.username)
#         return render_template('profile.html', dic=dic)
#     elif request.method == "POST":
#         keys = list(request.form)
#         pro_idx = find_index("pro", keys)
#         skill_idx = find_index("languages", keys)

#         basic_details = [request.form.get(key) for key in keys[:5]]
#         new_user_details = UserDetails(
#             username=current_user.username, full_name=basic_details[0], phone_number=basic_details[1], email=basic_details[2], linkedin=basic_details[3], github=basic_details[4])
#         db.session.merge(new_user_details)

#         college_details = [request.form.get(key) for key in keys[5:10]]
#         school_details = [request.form.get(key) for key in keys[10:15]]
#         new_education_details = Education(username=current_user.username, college=college_details[0], degree=college_details[1], cgpa=college_details[2], college_start=reverse_date(college_details[3]),
#                                           college_end=reverse_date(college_details[4]), school=school_details[0], board=school_details[1],
#                                           percentage=school_details[2], school_start=reverse_date(
#                                               school_details[3]), school_end=reverse_date(school_details[4]))
#         db.session.merge(new_education_details)

#         skill_details = [request.form.get(key)
#                          for key in keys[skill_idx:skill_idx+3]]
#         new_skill_details = Skills(username=current_user.username, languages=skill_details[0],
#                                    dev_tools=skill_details[1], frameworks=skill_details[2])
#         db.session.merge(new_skill_details)

#         coding_details = [request.form.get(key)
#                           for key in keys[skill_idx+3:skill_idx+6]]
#         new_coding_details = Coding(username=current_user.username, codechef=coding_details[0],
#                                     codeforces=coding_details[1], leetcode=coding_details[2])
#         db.session.merge(new_coding_details)

#         new_achievements = Achievements(
#             username=current_user.username, achievements=request.form.get(keys[-1]))
#         db.session.merge(new_achievements)
#         db.session.commit()

#         exp_details = [request.form.get(key) for key in keys[15:pro_idx]]
#         old_exp_datas = Experience.query.filter_by(
#             username=current_user.username).all()
#         for old_exp_data in old_exp_datas:
#             db.session.delete(old_exp_data)
#         for i in range(0, len(exp_details), 6):
#             new_exp = Experience(username=current_user.username, company_title=exp_details[i],
#                                  role=exp_details[i+1], tech_stack=exp_details[i+2], start_date=reverse_date(exp_details[i+3]), end_date=reverse_date(exp_details[i+4]), description=exp_details[i+5])
#             db.session.merge(new_exp)
#             db.session.commit()

#         pro_details = [request.form.get(key)
#                        for key in keys[pro_idx:skill_idx]]
#         old_pro_datas = Projects.query.filter_by(
#             username=current_user.username).all()
#         for old_pro_data in old_pro_datas:
#             db.session.delete(old_pro_data)
#         for i in range(0, len(pro_details), 6):
#             new_pro = Projects(username=current_user.username, project_title=pro_details[i],
#                                tech_stack=pro_details[i+1], project_link=pro_details[i+2], start_date=reverse_date(pro_details[i+3]), end_date=reverse_date(pro_details[i+4]), description=pro_details[i+5])
#             db.session.merge(new_pro)
#             db.session.commit()
#         flash('Successfully updated your profile!')
#         return redirect(url_for('main.profile'))


# @main.route('/<username>')
# def portfolio(username):
#     user = User.query.filter_by(username=username).first()
#     dic = generate_dict(username, disabled="disabled", hidden="is-hidden")
#     if user:
#         return render_template('portfolio.html', username=username, dic=dic)
#     return render_template('404.html', username=username)


# @main.route('/resume/<username>')
# def resume(username):
#     user = User.query.filter_by(username=username).first()
#     if user:
#         try:
#             base64_pdf = b""
#             os.makedirs(f'./portfolio-resume-builder/resume/{username}/')
#             dic = generate_dict(username, "", "", resume=True)
#             if create_resume(username, dic):
#                 subprocess.run(['pdflatex', '-interaction=nonstopmode',
#                                 f'-output-dir=./portfolio-resume-builder/resume/{username}', f"./portfolio-resume-builder/resume/{username}/resume.tex"])
#                 with open(f"./portfolio-resume-builder/resume/{username}/resume.pdf", "rb") as pdf_file:
#                     base64_pdf = base64.b64encode(pdf_file.read())
#             shutil.rmtree(f'./portfolio-resume-builder/resume/{username}/')
#             return render_template('resume.html', base64_pdf=base64_pdf.decode('ascii'), dic=dic)
#         except Exception as e:
#             print(e)
#             shutil.rmtree(f'./portfolio-resume-builder/resume/{username}/')
#     return render_template('404.html', username=username)


@main.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
