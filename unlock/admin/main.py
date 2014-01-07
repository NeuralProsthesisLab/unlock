from functools import wraps
from flask import request, Response, Flask, render_template, url_for
from sqlalchemy import create_engine

app = Flask(__name__)

host = 'ec2-54-204-43-139.compute-1.amazonaws.com'
name = 'dps7g4lruchrr'
user = 'wltunqpopbqexa'
port = '5432'
addr = 'EddWJaobEc8L1X-HvByJL3hODi'

#
def create_engine():
	engine = create_engine('postgresql://%s:%s@%s:%s/%s' % (user, addr, host, port, name))
	return engine

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'secret'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/secret-page')
@requires_auth
def secret_page():
	#return str(render_template)
	try:
		return render_template('main.html')
	except Exception as e:
		print("Exception = ", dir(e), e, e.__doc__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/hitmehard")
def ttol():
	import pyaudio
	import unlock
	# yous a do your business here...
	return str(dir(unlock))
		

if __name__ == "__main__":
    app.run()