#!/usr/bin/env python

import os
import http.server
import socketserver
from functools import partial

PORT = 8000

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')

Handler = partial(http.server.SimpleHTTPRequestHandler, directory=DOCS_DIR)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
