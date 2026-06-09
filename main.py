"""Main routes for course navigation and content viewing."""

import base64
import contextlib
import os
import shutil
import webbrowser
from pathlib import Path

import natsort
from flask import (
    Blueprint,
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required

from db_utility import (
    commit_current_course_details,
    commit_current_path_details,
    commit_current_user_details,
    get_current_course_details,
    get_current_path_details,
    get_current_user_details,
)
from os_utility import (
    build_folder_structure_for_monaco_sidebar,
    build_toc_render_items,
    check_code_present,
    create_dir,
    delete_dir,
    load_folder,
    load_toc_if_exist,
    load_topics,
)

main = Blueprint("main", __name__)
root_course_dir = os.getenv("COURSE_DIR", ".")
# Use environment variable or fall back to home directory
OS_ROOT = Path(
    os.environ.get("EDUCATIVE_VIEWER_ROOT", str(Path.home() / "EducativeViewer")),
)


@main.route("/")
def index() -> str:
    """Render the index page."""
    return render_template("index.html")


@main.route("/health")
def health() -> Response:
    """Health check endpoint for container orchestration."""
    return jsonify({"status": "healthy"})


@main.route("/courses", methods=["GET", "POST"])
@login_required
def courses() -> str | Response:  # noqa: C901, PLR0912, PLR0915
    """Handle course navigation and listing."""
    highlight_idx = None
    last_visited_topic = ""
    last_visited_index = 0
    course_dir = root_course_dir
    temp_folder_path = OS_ROOT / "temp" / current_user.username
    delete_dir(str(temp_folder_path))

    # Change the download button color based on the download access
    download_button_color = "#ed4444 !important"
    current_user_details = get_current_user_details(current_user.username)
    if current_user_details and current_user_details.downloadaccess:
        download_button_color = "#82f382 !important"

    current_path_details = get_current_path_details(current_user.username)
    if current_path_details is not None:
        course_dir = current_path_details.last_visited_directory
        last_visited_course = current_path_details.last_visited_course
        current_course_details = get_current_course_details(
            current_user.username,
            last_visited_course,
        )
        if current_course_details is not None:
            last_visited_topic = current_course_details.last_visited_topic
            last_visited_index = current_course_details.last_visited_index

    if request.method == "POST":
        if request.form.get("folder"):
            # Traversing in folders
            folder = request.form.get("folder")
            course_dir = str(Path(course_dir) / folder)
            folders = natsort.natsorted(list(Path(course_dir).iterdir()))
            folders = [f.name if hasattr(f, "name") else f for f in folders]
            last_visited_course = Path(course_dir).name
            current_course_details = get_current_course_details(
                current_user.username,
                last_visited_course,
            )
            if current_course_details is not None:
                last_visited_topic = current_course_details.last_visited_topic
                last_visited_index = current_course_details.last_visited_index
            if folder + ".html" in folders:
                # If topic.html is found, render the html then
                commit_current_course_details(
                    username=current_user.username,
                    last_visited_course=Path(course_dir).parent.name,
                    last_visited_topic=last_visited_topic,
                    last_visited_index=last_visited_index,
                )
                return redirect(url_for("main.courses") + f"/{folder}")
            if folder + ".html" not in folders:
                # It is a folder, traverse inside it.
                commit_current_path_details(
                    username=current_user.username,
                    last_visited_directory=course_dir,
                    last_visited_course=last_visited_course,
                )
                # If the last visited topic is present in the folder, highlight it.
                if last_visited_topic in folders:
                    highlight_idx = folders.index(last_visited_topic)

                # If table of contents.json is present, render using toc
                toc = load_toc_if_exist(course_dir)
                if toc:
                    toc_items = build_toc_render_items(toc, highlight_idx or 0)
                    return render_template(
                        "courses_toc.html",
                        toc_items=toc_items,
                        folder=folder,
                        download_button_color=download_button_color,
                    )
                return render_template(
                    "courses.html",
                    folder_list=folders,
                    folder=folder,
                    highlight_idx=highlight_idx,
                    download_button_color=download_button_color,
                )
        # If above condition doesnt satisfy then Traversing out folders
        if len(root_course_dir) < len(course_dir):
            course_dir = str(Path(course_dir).parent)
            folders = natsort.natsorted(load_folder(course_dir))
            last_visited_course = Path(course_dir).name
            commit_current_path_details(
                username=current_user.username,
                last_visited_directory=course_dir,
                last_visited_course=last_visited_course,
            )

            if last_visited_topic in folders:
                highlight_idx = folders.index(last_visited_topic)
            return render_template(
                "courses.html",
                folder_list=folders,
                folder=last_visited_course,
                highlight_idx=highlight_idx,
                download_button_color=download_button_color,
            )
    # GET request
    folders = natsort.natsorted(load_folder(course_dir))
    folder = Path(course_dir).name
    if last_visited_topic in folders:
        highlight_idx = folders.index(last_visited_topic)
    toc = load_toc_if_exist(course_dir)
    if toc:
        toc_items = build_toc_render_items(toc, highlight_idx or 0)
        return render_template(
            "courses_toc.html",
            toc_items=toc_items,
            folder=folder,
            download_button_color=download_button_color,
        )
    return render_template(
        "courses.html",
        folder_list=folders,
        folder=folder,
        highlight_idx=highlight_idx,
        download_button_color=download_button_color,
    )


@main.route("/courses/<topics>", methods=["GET", "POST"])
@login_required
def topics(topics: str) -> str | Response:  # noqa: C901
    """Handle topic viewing and navigation."""
    current_path_details = get_current_path_details(current_user.username)
    if current_path_details is None:
        return redirect(url_for("main.courses"))
    course_dir = current_path_details.last_visited_directory
    last_visited_course = current_path_details.last_visited_course
    current_course_details = get_current_course_details(
        current_user.username,
        last_visited_course,
    )
    if current_course_details is None:
        return redirect(url_for("main.courses"))
    topic_index = current_course_details.last_visited_index
    folders = natsort.natsorted(load_folder(course_dir))

    if topics in folders:
        topic_index = int(topics.split("-")[0])
        commit_current_course_details(
            username=current_user.username,
            last_visited_course=last_visited_course,
            last_visited_topic=topics,
            last_visited_index=topic_index,
        )
    itr = topic_index
    toc = load_toc_if_exist(course_dir)
    if toc:
        return _topics_toc(topics, course_dir, toc, itr)
    topic_folders = natsort.natsorted(load_topics(course_dir))
    with contextlib.suppress(ValueError):
        itr = int(topic_folders.index(topics))
    if request.method == "POST":
        if "back" in request.form and itr > 0:
            itr -= 1
        elif "next" in request.form and itr < len(topic_folders) - 1:
            itr += 1
        elif "sidebar-topic" in request.form:
            itr = int(request.form.get("sidebar-topic"))
        elif "home" in request.form:
            return redirect(url_for("main.courses"))
        elif request.form.get("code_filesystem"):
            path = f"file:///{course_dir}/{topic_folders[itr]}".replace("\\", "/")
            webbrowser.open(path)
    # GET request, this is used to refresh the webpage if required
    commit_current_course_details(
        username=current_user.username,
        last_visited_course=last_visited_course,
        last_visited_topic=topic_folders[itr],
        last_visited_index=itr,
    )

    # Calculate relative path for template
    if root_course_dir in {".", ""}:
        # Filter out '.', '/', and empty parts
        parts = [p for p in Path(course_dir).parts if p and p not in {".", "/"}]
        template_folder = "/".join(parts)
    else:
        relative_path = (
            course_dir[len(root_course_dir) :].lstrip(os.path.sep).lstrip("/")
        )
        template_folder = "/".join(relative_path.split(os.path.sep))
    webpage = f"{template_folder}/{topic_folders[itr]}/{topic_folders[itr]}.html"
    is_code_present = check_code_present(course_dir, topic_folders[itr])
    return render_template(
        "topics.html",
        code_present=is_code_present,
        webpage=webpage,
        folder=f"{topic_folders[itr]}",
        folder_list=topic_folders,
        itr=itr,
    )


def _topics_toc(  # noqa: C901, PLR0912
    topics: str,
    course_dir: str,
    toc: dict,
    itr: int,
) -> str | Response:
    """Handle topic viewing with table of contents navigation."""
    toc_items = build_toc_render_items(toc)
    with contextlib.suppress(StopIteration):
        itr = next(
            i for i, toc_item in enumerate(toc_items) if toc_item["title"] == topics
        )
    if request.method == "POST":
        if "back" in request.form and itr > 0:
            if toc_items[itr - 1]["is_category"]:
                if itr - 1 != 0:
                    itr -= 1
                else:
                    itr += 1
            itr -= 1
        elif "next" in request.form and itr < len(toc_items) - 1:
            if toc_items[itr + 1]["is_category"]:
                if itr + 1 != len(toc_items) - 1:
                    itr += 1
                else:
                    itr -= 1
            itr += 1
        elif "sidebar-topic" in request.form:
            itr = int(request.form.get("sidebar-topic"))
        elif "home" in request.form:
            return redirect(url_for("main.courses"))
        elif request.form.get("code_filesystem"):
            path = f"file:///{course_dir}/{toc_items[itr]['title']}".replace("\\", "/")
            webbrowser.open(path)

    # GET request, this is used to refresh the webpage if required
    last_visited_course = Path(course_dir).name
    topic_title = str(toc_items[itr]["title"])
    commit_current_course_details(
        username=current_user.username,
        last_visited_course=last_visited_course,
        last_visited_topic=topic_title,
        last_visited_index=itr,
    )

    # Calculate relative path for template
    if root_course_dir in {".", ""}:
        # Filter out '.', '/', and empty parts
        parts = [p for p in Path(course_dir).parts if p and p not in {".", "/"}]
        template_folder = "/".join(parts)
    else:
        relative_path = (
            course_dir[len(root_course_dir) :].lstrip(os.path.sep).lstrip("/")
        )
        template_folder = "/".join(relative_path.split(os.path.sep))
    webpage = f"{template_folder}/{topic_title}/{topic_title}.html"
    is_code_present = check_code_present(course_dir, topic_title)
    return render_template(
        "topics_toc.html",
        code_present=is_code_present,
        webpage=webpage,
        folder=topic_title,
        toc_items=toc_items,
        itr=itr,
    )


@main.route("/courses/code/<codes>", methods=["GET", "POST"])
@login_required
def codes(codes: str) -> str | Response:
    """Load the Monaco code editor for code/quiz files."""
    current_path_details = get_current_path_details(current_user.username)
    if current_path_details is None:
        return redirect(url_for("main.courses"))
    course_dir = current_path_details.last_visited_directory
    directory_path = str(Path(course_dir) / codes)
    encoded_path = base64.b64encode(directory_path.encode()).decode()
    return render_template("monaco-editor.html", encoded_path=encoded_path)


@main.route("/courses/list-files")
@login_required
def list_files() -> Response:
    """List all files for the Monaco sidebar."""
    encoded_path = request.args.get("encoded_path")
    directory_path = base64.b64decode(encoded_path.encode()).decode()
    files = build_folder_structure_for_monaco_sidebar(directory_path, directory_path)
    return jsonify(files)


@main.route("/courses/file-content/<path:filename>")
@login_required
def file_content(filename: str) -> Response:
    """Load file content for Monaco editor."""
    encoded_path = request.args.get("encoded_path")
    directory_path = base64.b64decode(encoded_path.encode()).decode()
    filename = base64.b64decode(filename.encode()).decode()
    file_path = Path(directory_path) / filename
    return send_file(str(file_path))


@main.route("/courses/download/<folder>", methods=["POST", "GET"])
@login_required
def download(folder: str) -> str | Response:
    """Download a course folder as a ZIP file."""
    course_dir = root_course_dir
    current_path_details = get_current_path_details(current_user.username)
    if current_path_details is not None:
        course_dir = current_path_details.last_visited_directory

    if request.method == "POST":
        if not current_user.downloadaccess:
            return render_template("downloadaccess.html")
        # Copy the course directory to temp folder and zip it
        temp_folder_path = OS_ROOT / "temp" / current_user.username / folder
        delete_dir(str(temp_folder_path))
        create_dir(str(temp_folder_path))
        temp_folder_course_dir = temp_folder_path / folder
        shutil.copytree(course_dir, str(temp_folder_course_dir))
        shutil.make_archive(
            str(temp_folder_course_dir),
            "zip",
            str(temp_folder_course_dir),
        )
        return redirect(
            url_for("main.courses") + f"/download-file/{folder}/{folder}.zip",
        )
    return redirect(url_for("main.courses"))


@main.route("/courses/download-file/<path:filepath>", methods=["POST", "GET"])
@login_required
def file_download(filepath: str) -> str | Response:
    """Serve a file for download."""
    temp_folder_path = OS_ROOT / "temp" / current_user.username
    try:
        return send_from_directory(str(temp_folder_path), filepath, as_attachment=True)
    except FileNotFoundError:
        return render_template("404.html", message="File does not exist")


@main.route("/courses/getdownloadaccess", methods=["POST", "GET"])
@login_required
def getdownloadacess() -> str | Response:
    """Handle download access token verification."""
    current_user_details = get_current_user_details(current_user.username)
    if current_user_details is None:
        return redirect(url_for("main.courses"))
    message = ""
    if request.method == "POST":
        downloadtoken = request.form.get("downloadtoken")
        if downloadtoken == os.getenv("DOWNLOADTOKEN", ""):
            current_user_details.downloadaccess = True
            commit_current_user_details(current_user_details)
            return redirect(url_for("main.courses"))
        message = "Please enter correct Download Token and try again."
    return render_template("downloadaccess.html", message=message)


@main.errorhandler(404)
def page_not_found(_error: Exception) -> tuple[str, int]:
    """Handle 404 errors."""
    return render_template("404.html", message="Page does not exist"), 404
