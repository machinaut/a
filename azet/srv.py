#!/usr/bin/env python

import http.server
import os
import socketserver
import threading
import time
from functools import partial

from azet import DOCS_DIR, NOTES_DIR
from azet.build import build, build_incremental

PORT = 8000


def watch_and_rebuild():
    """Watch for changes and rebuild when we get them"""
    last_mtimes = {}
    # Get last mtimes for all the notes
    for note_filename in os.listdir(NOTES_DIR):
        last_mtimes[note_filename] = os.path.getmtime(
            os.path.join(NOTES_DIR, note_filename)
        )
    # Loop forever, doing an incremental rebuild on files that update
    while True:
        time.sleep(0.1)
        # Check for changes
        for note_filename in os.listdir(NOTES_DIR):
            note_mtime = os.path.getmtime(os.path.join(NOTES_DIR, note_filename))
            if note_mtime > last_mtimes[note_filename]:
                print("Rebuilding {}".format(note_filename))
                build_incremental(note_filename)
                last_mtimes[note_filename] = note_mtime


if __name__ == "__main__":
    # Rebuild the whole site once
    build()

    # Launch a thread running the watch_and_rebuild function
    rebuild_thread = threading.Thread(target=watch_and_rebuild)
    rebuild_thread.daemon = True
    rebuild_thread.start()

    # Now start the server
    Handler = partial(http.server.SimpleHTTPRequestHandler, directory=DOCS_DIR)

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
