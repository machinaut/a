#!/usr/bin/env python

# %%
import os
import shlex
import shutil
from http.client import NOT_EXTENDED

from azet import DOCS_DIR, NOTES_DIR

NOTE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{id}</title>
</head>
<body>
<p>id: {id_link}</p>
<p>tags: {tag_links}</p>
<p>{body}</p>
</body>
"""

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Index</title>
</head>
<body>
<h1>Index</h1>
<h2>Tags</h2>
{tag_index}
<h2>Notes</h2>
{id_index}
"""


def build():
    """Build all the static pages"""
    # Clean up the old pages
    shutil.rmtree(DOCS_DIR)
    os.mkdir(DOCS_DIR)
    # Build the new pages
    notes = []
    for note_filename in os.listdir(NOTES_DIR):
        # Parse note file
        assert note_filename.endswith(".txt")
        note = parse(os.path.join(NOTES_DIR, note_filename))
        assert note_filename == note["id"] + ".txt", note_filename
        notes.append(note)
        # Build note page
        write(os.path.join(DOCS_DIR, note["id"] + ".html"), note)
    # Build the index page
    index(os.path.join(DOCS_DIR, "index.html"), notes)
    print("build")


def parse(note_path):
    """Parse a plain text note file into a dict"""
    note = {}
    with open(note_path, encoding="utf-8") as f:
        # id line
        id_line = f.readline()
        assert id_line.startswith("id:"), id_line
        note["id"] = id_line.replace("id:", "").strip()
        # tags line
        tags_line = f.readline()
        assert tags_line.startswith("tags:"), tags_line
        note["tags"] = shlex.split(tags_line.replace("tags:", "").strip())
        # note body
        note["body"] = f.read().replace("\n", "\n<br>")
    return note


def write(html_path, note):
    """Write an HTML page from a dict"""
    with open(html_path, "w", encoding="utf-8") as f:
        i = note["id"]
        id_link = f'<a href="/{i}.html">{i}</a>'
        tags_links = [f'<a href="/index.html#{t}">{t}</a>' for t in note["tags"]]
        tag_links = ", ".join(tags_links)
        f.write(
            NOTE_TEMPLATE.format(
                id=note["id"], id_link=id_link, tag_links=tag_links, body=note["body"]
            )
        )


def index(index_path, notes):
    """Generate and write the index html file"""
    with open(index_path, "w", encoding="utf-8") as f:
        # Build the tag index
        tag_index = "<h2>Tag Index</h2>"
        for tag in set(sum([n["tags"] for n in notes], [])):
            tag_link = f'<h3 id="{tag}"><a href="/index.html#{tag}">{tag}</a></h3>'
            tag_notes = []
            for note in sorted(notes, key=lambda n: n["id"]):
                if tag in note["tags"]:
                    i = note["id"]
                    id_link = f'<a href="/{i}.html">{i}</a>'
                    tag_notes.append(id_link)
            tag_index += tag_link + "<p>" + ", ".join(tag_notes) + "</p>"
        # Build the id index
        id_index = "<h2>Note Index</h2>"
        for note in sorted(notes, key=lambda n: n["id"]):
            i = note["id"]
            id_link = f'<a href="/{i}.html">{i}</a>'
            id_index += id_link + "<br>"
        # Write the index
        f.write("<h1>Index</h1>" + tag_index + id_index)


if __name__ == "__main__":
    build()
