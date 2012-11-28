import logging
from urlparse import urlparse

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from forms import URLform
from utils import get_source, slip

def home(request):
	context = RequestContext(request, {'form': URLform})
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
			return HttpResponseRedirect(reverse('slip_home_url'))
	if url != None:
		# hack'n'slash because of mod_wsgi rewrite rules that remove double 
		# slash after domain name
		if url[:7] != 'http://':
			url = 'http://' + url[6:]
			print url
		
		source = get_source(url)
		if source is None: 
			return HttpResponseRedirect(reverse('slip_home_url'))
		freudified = slip(source, url)
		if freudified is None:
			return HttpResponseRedirect(reverse('slip_home_url'))
		return HttpResponse(content=freudified)
		
		
	return HttpResponseRedirect(reverse('slip_home_url'))
