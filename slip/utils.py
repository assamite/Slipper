import os
import re
import operator
import urllib2
from urlparse import urljoin
from django.core.urlresolvers import reverse
from bs4 import BeautifulSoup as bs
from bs4 import CData
import nltk
import Levenshtein as lv
from Slipper import settings

import logging
import traceback

SEXWORDS = ""

repl_tags = {'NN':'n','JJ':'a','VB':'v','RB':'r'}

def get_source(url):
	'''
		Gets source code from 'url' and returns it if the page does not return
		HTML code >= 400. Otherwise returns None.
	'''
	
	logger = logging.getLogger('Slipper.slip')
	logger.info("Getting source from: %s" % url)
	try:
		response = urllib2.urlopen(url)
		logger.info("Got %s response from %s" % (response.getcode(), url))
	except:
		logger.error("Could not get source from: %s" % url)
		logger.error("Error stack \n %s" % traceback.format_exc())
		return None
	if response.getcode() > 399: 
		return None
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
	
	return s_words

def replace_document_words(words, tagged_words, sexws):
	'''
		Iterates over all the words in the document and finds suitable replacing 
		words for nouns, adjectives and adverbs from 'sexws'
	
		words:			list of tokenized raw words.
		tagged_words:	list of (raw word, tag) pairs
		sexws: 		dictionary of sexuality oriented words.
	
		Returns final altered document where all the found affect-wordnet's 
		positive-emotion words are changed to negative-emotion words and vice 
		versa.
	'''
	altered_words = []
	
	# magic numbers for max levenshtein distance. key: len(word), value: max lv
	maxlv = {3: 1, 4: 1, 5: 2, 6: 2, 7:2, 8: 3, 9: 3, 10: 3, 11: 3}
	alter_amount = 0

	for i, w in enumerate(words):
		altered_words.append(w)
		if len(w) < 3: continue
		tag = tagged_words[i][1][:2]
		if tag in ["NN", "JJ", "RB"]:
			tag = repl_tags[tag]
			lv = 1
			if len(w) in maxlv.keys(): lv = maxlv[len(w)]
			else: lv = 4
			rp = replace_word(lv, tag, w, sexws)	
			if not rp.lower() == w.lower():
				if w[0].isupper(): rp = rp.title()
				if settings.DEBUG: rp += " (" + w + ")"
				altered_words[i] = rp	
				alter_amount += 1
	#print "Altered %s words" % alter_amount
	return altered_words

def replace_word(maxlv, tag, word, sexws):
	'''
		Checks if there is suitable replace word in iterable.
	
		Parameters:
		maxlv: 	maximum levenshtein distance to be accepted from word and 
				replaced word
		tag:	word's position tag (noun, verb, etc)
		word:	word to find replace for
		sexws:	iterable to find replace word from.
		
		Returns word if no replace word is found, otherwise returns word to 
		replace original word in the text (closest by levenshtein distance).
	'''
	
	levenshteins = []
	for sexw in sexws[tag]:
		levenshteins.append((sexw, lv.distance(word, sexw)))
	levenshteins = sorted(levenshteins, key=operator.itemgetter(1))
	if levenshteins[0][1] <= maxlv: # Let's take first one always. It's good
		return levenshteins[0][0]	# to be coherent with these, so that some 
	else:							# sense is maintained in the text.
		return word

def prettify_sentence(replaced_words):
	pretty_sentence = ""
	last_word = ""
	enc_hyphen = False
	
	for w in replaced_words:
		if w in ["``", "\""]:
			pretty_sentence += " \""
		elif w == "''":
			pretty_sentence += "\""
		elif w in [',', '!', '?', '.', '%', '\"', "n't", "'re", "'s", ";", ":", ")", "]", "}", "'m", "'ll", "'s", "'d"]:
			pretty_sentence += w
		elif w in ['\'']: 
			if enc_hyphen:
				pretty_sentence += w
				enc_hyphen = False	
		elif last_word in ["``", "(", "[", "{", "\""]:
			pretty_sentence += w	
		else:
			pretty_sentence += " " + w
		if w.startswith("'") and w not in ["'m", "'d", "'re", "'s", "'ll"]: 
			enc_hyphen = True
		last_word = w
	
	return pretty_sentence
	
# TODO: FIX ME, probably not everything is correct in here.	
def visible_html_tag(element):
	'''
		Checks if given element in soup parsed by BeautifulSoup is visible to 
		the site's viewer or not.
		
		Parameters:
		element:	element to be checked
		
		Returns true if element is visible, otherwise not.
	'''
	if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
		return False
	if element.name in ['script']: 
		return False
		'''
		if element.name and 'style' in element.attrs:
			#print element['style']
			if re.match(r'display:(\s*)none', element['style']):
				return False
		if element.parent.name and 'style' in element.parent.attrs:
			print element.parent['style']
			if re.match(r'display:(\s*)none', element.parent['style']):
				return False
		'''
	elif re.match(u'.*<!--.*-->.*', str(element), re.DOTALL):
		return False
	return True

def fix_relative_paths(soup, url):
	'''
		Change relative paths from soup's tags to absolute paths. 
		
		Fixes href's from all tags, and changes all href's from 'a'-tags to be
		forwarded via the freudifier site. Also changes src's from script-tags
		and searches all media-tags' contents form r'@inform "(.*)"' patterns
		which are then changed to absolute paths. Absolute path-changing is done
		by urlparse.urljoin. (This does not solve all the paths, but some amount
		none the less)
		
		Fixes the paths, etc. in place, so the given soup is altered.
		
		Parameters:
		soup: 	HTML soup parsed by BeautifulSoup
		url:	base url of the site
	'''
	
	# fix relative paths. Horrible code.
	for t in soup.html.descendants: 
		if not hasattr(t, 'name'): continue
		if 'href' in t.attrs:
			t['href'] = urljoin(url, t['href'])
		if t.name == 'a' and 'href' in t.attrs:
			t['href'] = reverse('slip_freudify_url', kwargs = { 'url': t['href'] })
		if 'src' in t.attrs:
			t['src'] = urljoin(url, t['src'])
			
		# TODO: FIX ME, there must be better way for this.
		if t.name == 'style' and hasattr(t, 'contents'):
			cat = []
			for c in t.contents:
				# First find the '@import "(.*)"' and then find the pattern 
				# inside "". Does not actually fix the imports in place, but 
				# adds absolute paths at the end of the t.string.
				for m in re.finditer(r"@import(\s+)\"(.*)\"", c):
					for n in re.findall(r"\"(.*)\"", m.group()): 
						cat.append("@import \"%s\";" % urljoin(url, n))
			t.string = t.string + " " + " ".join([w for w in cat])
				
def freudify_soup(soup):
	'''
		Freudifies all given soup's visible text.
		
		Does not consider texts that have less than three words.
		
		Parameters:
		soup:	HTML soup parsed by BeautifulSoup.
		
		Returns freudified soup.
	'''
	
	for t in soup.body.descendants:
		if not hasattr(t, 'name'): continue

		if visible_html_tag(t) and hasattr(t, 'string'):
			if t.string == None: continue
			if isinstance(t, CData): 
				print "buu"
				continue
			#if t.string.startswith("[CDATA["): continue
			sentences = nltk.sent_tokenize(t.string)
			replaced_string = ""
			for s in sentences:
				tx = nltk.word_tokenize(s)
				if len(tx) < 3: continue
				tagged_text = nltk.pos_tag(tx)
				if len(tagged_text) < 3: continue
				replaced = replace_document_words(tx, tagged_text, SEXWORDS)
				replaced_string += " " + prettify_sentence(replaced)
			if len(replaced_string) > 0:
				t.string = replaced_string

def slip(source, url):
	'''
		Main function to call. Freudifies the given HTML source code and fixes 
		all the relative path's in the source code to start with 'url'. 
		
		Basically calls BeautifulSoup to soup the source and then calls 
		fix_relative_paths and freudify_soup
		
		Parameters:
		source:		source code of the site
		url:		url of the site
		
		Returns changed source code.
	'''
	soup = bs(source)
	logger = logging.getLogger('Slipper.slip')
	
	try:
		fix_relative_paths(soup, url)
		freudify_soup(soup)
	except:
		logger.info("utils.slip has blown, with message: \n %s" % traceback.format_exc())
		return None
		
	logger.info("Finished tagging source from: %s " % url)
	return soup.prettify()

SEXWORDS = read_wordnet_sexuality(os.path.join(settings.SITE_ROOT, "slip", "sexuality.txt"))