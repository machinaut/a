#!/usr/bin/env python

import os
import http.server
import socketserver
from functools import partial
from azet import DOCS_DIR

PORT = 8000

Handler = partial(http.server.SimpleHTTPRequestHandler, directory=DOCS_DIR)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
