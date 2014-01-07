from flask import request, Response, Flask, render_template, url_for
app = Flask(__name__)

import admin.auth