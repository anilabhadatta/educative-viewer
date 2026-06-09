"""Filesystem utility functions for course directory operations."""

import base64
import json
import shutil
from pathlib import Path


def delete_dir(path: str) -> None:
    """Delete a directory and all its contents."""
    dir_path = Path(path)
    if dir_path.exists():
        shutil.rmtree(dir_path)


def create_dir(path: str) -> None:
    """Create a directory if it doesn't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)


def load_folder(path: str) -> list[str]:
    """Load list of items in a folder."""
    folder_path = Path(path)
    return [item.name for item in folder_path.iterdir()]


def load_topics(course_dir: str) -> list[str]:
    """Load list of topic folders from a course directory."""
    course_path = Path(course_dir)
    return [
        folder.name
        for folder in course_path.iterdir()
        if folder.is_dir() and (folder / f"{folder.name}.html").is_file()
    ]


def load_toc_if_exist(course_dir: str) -> dict[str, object] | None:
    """Load table of contents JSON if it exists."""
    if not course_dir:
        return None
    toc_path = Path(course_dir) / "__toc__.json"
    if toc_path.exists():
        return json.loads(toc_path.read_text())
    return None


def check_code_present(course_dir: str, topic: str) -> bool:
    """Check if code files exist for a topic."""
    topic_path = Path(course_dir) / topic
    if not topic_path.exists():
        return False
    for item in topic_path.iterdir():
        if item.is_file() and item.name != f"{topic}.html":
            return True
    return False


def build_toc_render_items(
    toc: dict[str, object],
    highlight_idx: int = 0,
) -> list[dict[str, object]]:
    """Build renderable items from table of contents."""
    toc_items: list[dict[str, object]] = []
    curr_topic_idx = 0
    toc_list: list[object] = toc.get("toc", [])
    for item in toc_list:
        if isinstance(item, dict):  # category
            toc_items.append(
                {
                    "title": item["category"],
                    "is_category": True,
                    "color": "white",
                    "focus": "",
                },
            )
            for topic in item["topics"]:
                temp_map: dict[str, object] = {
                    "title": topic[1],
                    "is_category": False,
                    "color": "white",
                    "focus": "",
                }
                if curr_topic_idx == highlight_idx:
                    temp_map["color"] = "#0dfd10"
                    temp_map["focus"] = "focus-button"
                toc_items.append(temp_map)
                curr_topic_idx += 1
        else:  # assessments, projects, cloud labs..
            temp_map = {
                "title": item[1],
                "is_category": False,
                "color": "white",
                "focus": "",
            }
            if curr_topic_idx == highlight_idx:
                temp_map["color"] = "#0dfd10"
                temp_map["focus"] = "focus-button"
            toc_items.append(temp_map)
            curr_topic_idx += 1
    return toc_items


def build_folder_structure_for_monaco_sidebar(
    directory: str,
    root: str,
) -> list[dict[str, object]]:
    """Build folder structure for Monaco editor sidebar."""
    structure: list[dict[str, object]] = []
    dir_path = Path(directory)

    for item in dir_path.glob("*"):
        if item.is_dir():
            node: dict[str, object] = {"text": item.name, "nodes": []}
            # Recursively build structure for subfolder
            substructure = build_folder_structure_for_monaco_sidebar(str(item), root)
            if substructure:
                node["nodes"].extend(substructure)
            structure.append(node)
        elif item.is_file():
            filename = item.name
            if filename != f"{item.stem}.html":
                file_path = item.relative_to(root)
                encoded_path = base64.b64encode(str(file_path).encode()).decode()
                structure.append(
                    {
                        "text": filename,
                        "type": "file",
                        "encoded_path": encoded_path,
                    },
                )

    return structure
