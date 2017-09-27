# coding: utf-8

# Imports
from flask import Flask, url_for, render_template, \
				  redirect, request, Markup
from flask_sqlalchemy import SQLAlchemy
from urlparse import urlparse

import requests

# Instantiate
app = Flask(__name__)
app.config.from_pyfile("config.py")
db = SQLAlchemy(app)

# Models
class KeyLink(db.Model):

	# Template
	__tablename__ 	= "links"
	id 				= db.Column("links_id", db.Integer, primary_key=True)
	keyword 		= db.Column(db.String(255))
	url 			= db.Column(db.String)

	# Constructor
	def __init__(self, keyword, url):
		self.keyword 	= keyword
		self.url 		= url

# Routes
# Index
@app.route("/")
def index():
	return render_template("index.html") 

# About
@app.route("/about")
def about():
	return render_template("about.html")

# Get Link
@app.route("/query", methods=["GET"])
def query_link():

	# GET Request
	if request.method == "GET":

		# Get Keyword Paramater from URL
		keyword = request.args.get("kw")

		# Keyword Paramater Not Specified
		if keyword is None or keyword == "":
			return render_template("query.html",  text="Keyword Paramater Not Specified")

		# Keyword Found for Lookup
		else:

			keyword = keyword.encode("utf-8")

			# Get Link Record from DB
			link = KeyLink.query.filter_by(keyword=keyword).first()

			# Check Link Record Exists in DB
			if link is None:
				return render_template("query.html",  text="Keyword \"{}\" Not Found in Goon Database".format(keyword))

			# Found Record now Redirect
			else:
				return redirect(link.url)

# Add Link
@app.route("/add", methods=["POST"])
def add_link():

	# POST Request
	if request.method == "POST":

		# Get Form Parameters
		keyword	= request.form.get("keyword").encode("utf-8")
	 	url		= request.form.get("url").encode("utf-8")
	 	force 	= "no"
	 	text 	= ""
	 	error  	= False

	 	# Check Empty Keyword
	 	if keyword == "":
			error = True; text = "Keyword Field Empty"; force = "no"
	 		
	 	# Check Empty URL
	 	elif url == "":
			error = True; text = "URL Field Empty"; force = "no"

	 	# Prevent Duplicate Keyword
	 	elif KeyLink.query.filter_by(keyword=keyword).first():
	 		
	 		# Get Link
	 		link = KeyLink.query.filter_by(keyword=keyword).first()
			error = True; text = "Keyword Already Associated with URL"; force = "no"
	 	
	 	# Prevent Duplicate URL
	 	elif KeyLink.query.filter_by(url=url).first():
	 		
	 		# Get Link
	 		link = KeyLink.query.filter_by(url=url).first()
			error = True; text = "URL Already Associated with Keyword \"{}\"".format(link.keyword); force = "no"
	 	
		# Add New URL
		else:

	 		# Check Force URL is Set
	 		if request.form.get("force") and request.form.get("force").encode("utf-8") == "yes":

	 			# Fix Case
				keyword = keyword.decode("utf-8").lower()
				url = url.decode("utf-8")

				# Valid 
				new_link = KeyLink(keyword, url)
				db.session.add(new_link)
				db.session.commit()

			else:

				# Validate URL
				try:

					# Parse URL
					parsed_url = urlparse(url)

					# Bad Scheme
					if parsed_url.scheme.lower() != "http" and parsed_url.scheme.lower() != "https":
						error = True; text = "Invalid URL Scheme"; force = "no"
					
					# Bad Netloc
					elif parsed_url.netloc.lower() == "":
						error = True; text = "Invalid URL Location"; force = "yes"

					# Valid URL
					else:

						# Make Request
						r = requests.get(url, timeout=5, allow_redirects=True)

						# Check 404
						if r.status_code == 404:
							error = True; text = "404 Error Occured"; force = "yes"
						else:
							# Fix Case
							keyword = keyword.decode("utf-8").lower()
							url = url.decode("utf-8")

							# Valid 
							new_link = KeyLink(keyword, url)
							db.session.add(new_link)
							db.session.commit()

				# Connection Error
				except requests.exceptions.ConnectionError:
					error = True; text = "URL Connection Error"; force = "yes"
					
				# Timed Out
				except requests.exceptions.Timeout:
					error = True; text = "URL Timed Out"; force = "yes"

				# Too Many Redirects
				except requests.exceptions.TooManyRedirects:
					error = True; text = "Too Many Redirects"; force = "yes"

				# Everything Else
				except:
					error = True; text = "Unknown URL Error"; force = "yes"

		if error:
			if force and force == "yes":
				return render_template("query.html", text=text, force=force, keyword=keyword, url=url)
			else:
				return render_template("query.html", text=text, force=force)
		else:
			return render_template("query.html",  text="Successfully Added Keyword \"{}\"".format(keyword))

# Delete Link
@app.route("/delete", methods=["GET"])
def delete_link():

	# DELETE Request
	if request.method == "GET":

		# Get Form Parameters
		keyword	= request.args.get("keyword").encode("utf-8")

		# Check Keyword Exists
	 	if not KeyLink.query.filter_by(keyword=keyword).first():
	 		return render_template("query.html",  text="Keyword Not Found")

	 	# Get Link
	 	link = KeyLink.query.filter_by(keyword=keyword).first()

	 	# Delete
	 	db.session.delete(link)
	 	db.session.commit()
	 	
	 	return redirect(url_for("list"))

# Keyword List
@app.route("/list")
def list():

	# Get Links
	links = KeyLink.query.all()

	# Empty List
	if not links:
		return render_template("list.html",  empty=True)
		
	return render_template("list.html",  links=links)

# Entry Point
if __name__ == "__main__":
	app.run()
