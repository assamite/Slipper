import os
import re
import sys
import operator
import random
import urllib2
from bs4 import BeautifulSoup as bs
import nltk
import Levenshtein as lv
from slipper import settings

import logging
import traceback

SEXWORDS = ""

repl_tags = {'NN':'n','JJ':'a','VB':'v','RB':'r'}

def get_source(url):
	response = urllib2.urlopen(url)
	page_source = response.read()
	return page_source

def read_wordnet_sexuality(filepath):
	'''
		Reads 'sexuality.txt' and puts it in s_words dictionary. 
	'''
	
	f = open(filepath)
	s_words = {}

	for l in f.readlines():
		t = l.split()
		tag = t[0][0]
		ws = t[1:]
		for w in ws:
			w = unicode(w.replace('_', ' '), "UTF-8")
			s_words[w] = tag
			try:
				s_words[tag].append(w)
			except KeyError:
				s_words[tag] = [w]
				
#	for k,v in s_words.items():
#		print k, [w for w in v]
		
	return s_words
		
def position_tag_text(text):
	return nltk.pos_tag(nltk.word_tokenize(text))
	
	

def replace_document_words(words, tagged_words, s_words):
	'''
		Main loop of the algorithm. Iterates over all the words in the document 
		and finds suitable replacing words for nouns, adjectives and adverbs 
		with parent category in 'negative-emotion' or 'positive-emotion'
	
		words:			list of tokenized raw words.
		tagged_words:	list of (raw word, tag) pairs
		affect_words: 	dictionary of affect words. key: word, value: list
						[id, tag, specific category, parent category]
	
		Returns final altered document where all the found affect-wordnet's 
		positive-emotion words are changed to negative-emotion words and vice 
		versa.
	'''
	altered_words = []
	alter_amount = 0

	for i, w in enumerate(words):
		altered_words.append(w)
		if len(w) < 3: continue
		tag = tagged_words[i][1][:2]
		if tag in ["NN", "JJ", "RB"] :
			tag = repl_tags[tag]
			rp = test_levenshtein(2, tag, w, s_words)	
			if not rp == w:
				altered_words[i] = rp + " (" + w + ")"
				alter_amount += 1
	print "Altered %s words" % alter_amount
	return altered_words

def test_levenshtein(maxlv, tag, word, sexws):
	levenshtains = []
	for sexw in sexws[tag]:
		levenshtains.append((sexw, lv.distance(word, sexw)))
	levenshtains = sorted(levenshtains, key=operator.itemgetter(1))
	if levenshtains[0][1] <= maxlv:
		#print word, levenshtains[0]
		return levenshtains[0][0]
	else:
		return word
	
def visible(element):
	if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
		return False
	elif re.match(u'.*<!--.*-->.*', str(element), re.DOTALL):
		return False
	return True

def slip(source, url):
	SEXWORDS = read_wordnet_sexuality(os.path.join(settings.SITE_ROOT, "slip", "sexuality.txt"))
	soup = bs(source)
	logger = logging.getLogger('slipper.slip')
	
	try:
		for t in soup.body.descendants:
			if not hasattr(t, 'name'): continue
			#t.string = t.replace(u'\xa0', u' ')
			if visible(t) and hasattr(t, 'string'):
				if t.string == None: continue
				tx = nltk.word_tokenize(t.string)
				if len(tx) < 3: continue
				tagged_text = nltk.pos_tag(tx)
				if len(tagged_text) < 3: continue
				replaced = replace_document_words(tx, tagged_text, SEXWORDS)
				t.string = "".join([w+" " for w in replaced])
	except:
		logger.info("utils.slip has blown, with message: \n %s" % traceback.format_exc())
		
	logger.info("Finished tagging source from: %s " % url)
	return soup.prettify()

#SEXWORDS = read_wordnet_sexuality("./sexuality.txt")