What?
=====

Small project for "mirroring" websites and adding some "humorous" content to them.

Freudifier is made with Django and the app structure is made to be compatible with Heroku.

Where?
======

Working version can be found at: http://freudifier.herokuapp.com

How?
====

Basically the application gets the source code of the typed URL, then parses it
with beautifulsoup, changes "all" (working on it) the relative paths to absolute
paths and all the links to go via the application's site. Then it does part of 
speech tagging of webpage's visible text with nltk and replaces words depending on 
the part of speech and levenshtein distance to another words from sexuality.txt.

Setup:

* Setup GIT, obviously.

* Clone this repository locally.

* Download virtualenv and read the documentation (basically activate/deactivate):
	http://www.virtualenv.org/en/latest/

* Create new virtual environment to this folder by:
	$ virtualenv venv
	
	If you use another name, remember to add it to .gitignore
	
* Activate virtual environment (type 'deactivate' to exit venv):
	$ source venv/bin/activate
	
* Download all the requirements for the project with:
	$ pip install -r requirements.txt
	
* If you don't have nltk installed before this you can either:
	1.) Use nltk.download() to download all the data
	2.) Change environment variable $NLTK_DATA to represent nltk_data folder.
	
* Go to freudifier-folder:
	$ python manage.py runserver
	
	Stop it with CTRL-C
	
* Then you can access the webpage in your browser:
	http://127.0.0.1:8000/
	
Hopefully I didn't miss a step in here.
	


