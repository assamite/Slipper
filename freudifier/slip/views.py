import logging
from urlparse import urlparse

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from forms import URLform
from utils import get_source, slip

def home(request, msg = None):
	if msg is None: msg = "Enter an URL of an english web page."
	#if not isinstance(msg, str): msg = ""
	context = RequestContext(request, {'form': URLform, 'msg': msg})
	return render_to_response('home.html', context)

def freudify(request, url = None):
	'''
		Handles freudifying of the url it gets as POST-data. 
	'''
	if request.method == 'POST':
		form = URLform(request.POST)
		if form.is_valid():
			url = request.POST['url']  
		else:
			return home(request, "Not a valid POST-data. Check the URL.")
	if url != None:
		# hack'n'slash because of mod_wsgi rewrite rules that remove double 
		# slashes after domain name
		if url[:7] != 'http://':
			url = 'http://' + url[6:]
		
		source = get_source(url)
		if source is None: 
			return home(request, "An error happened while trying to retrieve source from %s" % url)
		if isinstance(source, int): 
			return home(request, "%s returned %s" % (url, source))
		freudified = slip(source, url)
		if freudified is None:
			return home(request, "Encountered an error while freudifying %s" % url)
		return HttpResponse(content=freudified)
			
	return HttpResponseRedirect(reverse('slip_base_url'))
