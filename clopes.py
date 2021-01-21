import os
import sys
import time
import datetime
import sqlite3
from flask import Flask, request, redirect, url_for, render_template, abort, Markup, make_response, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__, static_url_path='/static')
app.url_map.strict_slashes = False

@app.route('/', methods=['GET'])
def download():
    return render_template("index.html")

print("[+] listening")
app.run(host="0.0.0.0", port=2005, debug=True)

