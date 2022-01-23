#!/usr/bin/env python
import os
import shlex
import shutil

from azet import DOCS_DIR, NOTES_DIR

NOTE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{id}</title>
</head>
<body>
<h2>{title}</h2>
<p>{body}</p>
<p>tags: {tag_links}</p>
<p>id: {id_link}</p>
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
    # Build the new pages
    notes = parse_notes()
    for note in notes:
        write(os.path.join(DOCS_DIR, note["id"] + ".html"), note)
    # Build the index page
    index(os.path.join(DOCS_DIR, "index.html"), notes)


def build_index():
    """Rebuild the index file"""
    # Build the new pages
    notes = parse_notes()
    # Build the index page
    index(os.path.join(DOCS_DIR, "index.html"), notes)


def build_incremental(note_filename):
    """Rebuild just a single note and then the index"""
    note = parse(os.path.join(NOTES_DIR, note_filename))
    write(os.path.join(DOCS_DIR, note["id"] + ".html"), note)
    build_index()


def parse_notes():
    """Parse all of the notes, returning a list of dicts"""
    notes = []
    for note_filename in os.listdir(NOTES_DIR):
        # Parse note file
        assert note_filename.endswith(".txt")
        note = parse(os.path.join(NOTES_DIR, note_filename))
        assert note_filename == note["id"] + ".txt", note_filename
        notes.append(note)
    return notes


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
        # title line
        title_line = f.readline()
        assert title_line.startswith("title:"), title_line
        note["title"] = title_line.replace("title:", "").strip()
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
                id=note["id"], id_link=id_link, tag_links=tag_links, title=note["title"], body=note["body"]
            )
        )


def index(index_path, notes):
    """Generate and write the index html file"""
    with open(index_path, "w", encoding="utf-8") as f:
        # Build the tag index
        tag_index = "<h2>Tag Index</h2>"
        # Each tag has its own list of notes
        for tag in set(sum([n["tags"] for n in notes], [])):
            tag_link = f'<div id="{tag}"><b><a href="/index.html#{tag}">{tag}</a></b>'
            tag_notes = []
            for note in sorted(notes, key=lambda n: n["id"]):
                if tag in note["tags"]:
                    id_link = f'<li><a href="/{note["id"]}.html">{note["id"]}</a>: {note["title"]}</li>'
                    tag_notes.append(id_link)
            tag_list = "<ul>" + "\n".join(tag_notes) + "</ul>"
            tag_index += tag_link + tag_list + '</div>'
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
