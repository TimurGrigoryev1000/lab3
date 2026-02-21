from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello_sysc3010():
	return "<p>SYSC3010 rocks!</p>"
@app.route("/hello")
def hello_page():
	name =  "Timur"
	return render_template("hello.html", name=name)


if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)

