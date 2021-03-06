Freudian Slipper
================

Small project for "mirroring" websites and adding some "humorous" content to them.

Freudifier is made with [Django](https://www.djangoproject.com/) 1.3.1 and the app 
structure is made to be compatible with [Heroku](http://www.heroku.com/). 
Currently app is coded with python 2.7.1 (though Heroku uses 2.7.2).

Where?
------

Working version can be found at: http://freudifier.herokuapp.com

How?
----

Basically the application gets the source code of the typed URL, then parses it
with [beautifulsoup](http://www.crummy.com/software/BeautifulSoup/), changes "all" 
(working on it) relative paths to absolute
paths and all the links to go via the application's site. Then it does part of 
speech tagging of webpage's visible text with [nltk](http://nltk.org/) and replaces words depending on 
the part of speech and [Levenshtein distance](http://en.wikipedia.org/wiki/Levenshtein_distance) 
to some other words found from the database. This is somehow supposed to be funny.

Most original tarts of the application can be found from [freudifier/slip/utils.py](https://github.com/assamite/Slipper/blob/master/freudifier/slip/utils.py)

Setup
-----

Here are the setup steps you need to take to make this app running on your local computer.
Instructions are mainly for Unix based operating system, for Windows you have to figure them
out yourself, as I don't have much experience in developing on it.
For more thorough information of used technologies check the technologies' own documentations.

[Setup GIT](https://help.github.com/articles/set-up-git) and python 2.7.x obviously.

Clone this repository locally.

	$ git clone https://github.com/assamite/Slipper.git

Download [virtualenv](http://www.virtualenv.org/en/latest/) and read the documentation (basically activate/deactivate)
	
Create new virtual environment to this folder.
	
	$ virtualenv venv
	
*If you use another name, remember to add it to ``.gitignore``.*
	
Activate virtual environment.
	
	$ source venv/bin/activate
	
Download all the requirements for the project with:
	
	(venv)$ pip install -r requirements.txt
	
If you don't have nltk installed before this you can either:

Download needed nltk data

	$ python
	>>> import nltk
	>>> nltk.download()
	
This should open a downloader which you can use to download needed data files.
Currently app is only using punkt-tokenizer with english pickle and maxent treebank pos tagger 
also with english pickle. You can of course download all the data if you want, but it will take 
some time and disc space.

**Or** you can change environment variable ``$NLTK_DATA`` to represent ``nltk_data/``. 

	(venv)$ NLTK_DATA=path/to/project/root/nltk_data/
	
If you are using [virtualenvwrapper](http://www.doughellmann.com/projects/virtualenvwrapper/) it is recommended to add above mentioned line to ``venv/bin/postactivate``,
otherwise you have to set the variable every time you activate ``venv``.

Get [SQLite3](http://www.sqlite.org/) or some other database and set it up. 
If you use other type of database, check Django's documentation about it. Settings up the sqlite3 database is easy.

	$ cd freudifier
        $ sqlite3 freudifier.db
        >.quit

**Remember** to add the sqlite database file to ``.gitignore`` if you are using other file place/name than ``freudifier/freudifier.db``.
The basic configurations in ``settings.py`` point to that file. 

Now you have to create needed database tables and populate tables with initial data.
	
	$ python manage.py syncdb
	$ python manage.py loaddata freudifier_noun.json
	$ python manage.py loaddata freudifier_adverb.json
	$ python manage.py loaddata freudifier_adjective.json
	$ python manage.py loaddata freudifier_verb.json
	
``syncdb`` will probably ask you about creating a new superuser. This is recommended as you can access
http://site.root.url/admin/ with it.
Now you should have all the requirements installed, nltk should be able to find needed data and database
should be ready and filled with initial data.
After this you just have to run the Django's development server to be able to access site on your
local browser.

	(venv)$ cd freudifier
	(venv)$ python manage.py runserver
	
*(Stop it with CTRL-C)*
	
Then you can access the webpage in your browser: http://127.0.0.1:8000/
Remember to always activate virtualenv before trying to run the server!	

When you are *not* currently anymore running the project you can exit virtual environment.
	
	(venv)$ deactivate
	
-- S.L 

ps. Hopefully I didn't miss a step in here.	


