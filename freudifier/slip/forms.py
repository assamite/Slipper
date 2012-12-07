'''
Created on Nov 27, 2012

@author: slinkola
'''

from django import forms

class URLform(forms.Form):
	'''
		Simple form to get URL of the desired web site.
	'''
	url = forms.URLField(initial= "http://", label = "")