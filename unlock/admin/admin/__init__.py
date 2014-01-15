from flask import request, Response, Flask, render_template, url_for
app = Flask(__name__, template_folder='template')

import admin.database
import admin.authorization
import admin.unlock
import admin.research