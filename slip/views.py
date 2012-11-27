from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from forms import URLform
from utils import get_source, slip

def home(request):
	context = RequestContext(request, {'form': URLform})
	return render_to_response('home.html', context)

def freudify(request):
	'''
		Handles freudifying of the url it gets as POST-data. 
	'''
	if request.method == 'POST':
		form = URLform(request.POST)
		if form.is_valid():
			url = request.POST['url']  
			source = get_source(url)
			freudified = slip(source, url)
			return HttpResponse(content=freudified)
			#return HttpResponseRedirect(url)

	return render_to_response('home.html')