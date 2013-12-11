from flask import Flask
app = Flask(__name__)

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