'''	Small "humorous" nltk/wordnet script. 

	Script changes all the positive and negative emotion words that are both
	in the given document and in the wordnet-affect's word list to some other
	word from the other category (positive emotions are changed to negative
	emotions and vice versa).
	
	You need to have nltk installed and nltk.corpus.wordnet data downloaded.
	
	Script presumes that 'wordnet-affect'-folder under running directory 
	contains following files:
		a-hierarchy.xml
		a-synsets.xml
		id-syns-list.txt
		
	To run the script:
		>python ./replacer.py [v] <filepath to raw text document> 
		v - optional argument for verbose output.
'''

import sys
import operator
import random
import nltk
import Levenshtein as lv
from nltk.corpus import wordnet as wn
import xml.etree.ElementTree as ET

VERBOSE = False

# Some replacing tags for passing the words to wordnets (affect and basic nltk)
# and back. Not needed at the moment.
morph_tags = {'n':wn.NOUN,'a':wn.ADJ,'v':wn.VERB,'r':wn.ADV}
repl_tags = {'NN':'n','JJ':'a','VB':'v','RB':'r'}

# affect-wordnet's synsets xml as an element tree and it's root
a_synsets = ET.parse('./wordnet-affect/a-synsets.xml')
as_root = a_synsets.getroot()

# affect-wordnet's hierarhy xml as an element tree and it's root
a_hierarchy = ET.parse('./wordnet-affect/a-hierarchy.xml')
ah_root = a_hierarchy.getroot()


def find_categ(id, tag = "noun-syn"):
	''' 
		Find word's affection category by its id
		
		Returns tuple (tag, category string)
	'''
	for child in as_root:
		for c in child: 
			if id == c.attrib['id']: 
				
				if 'categ' not in c.attrib:
					return find_categ(c.attrib['noun-id'], c.tag)
				else: return (tag, c.attrib['categ'])
	return ("", "")

def find_parent(name, root = ah_root, categories = ['positive-emotion', 'negative-emotion']):
	'''
		Find affect-wordnet's words' parent category from category list. 
		
		name: 		category name
		root: 		root to start searching from, defaults to 'ah_root'.
		categories: list of possible parent category candidates, defaults to
					['positive-emotion', 'negative-emotion']
		returns: 	parent category from 'categories' as str or empty string if 
					no category is found.
	'''
	for child in root:
		if child.attrib['name'] == name:
			if ('isa' in child.attrib) and (child.attrib['isa'] in categories):
				return child.attrib['isa']
			elif 'isa' not in child.attrib:
				return "" 
			else: return find_parent(child.attrib['isa'])
	return ""

def replace_with(tag, category):
	'''
		Find suitable replacing word from word category.
		The actual replacing word is decided by random from all the candidates.
		
		tag: 		in {noun-syn, adj-syn, adv-syn, verb-syn}
		category:	name of the category to find possible replacing words from
		returns: 	replacing word as str
	'''
	ws = []
	for k, v in a_words.items():
		if v[1] == tag and v[3] == category:
				ws.append(k)
	return ws[random.randint(0, len(ws)-1)]

def read_wordnet_affect():
	'''
		Reads wordnet-affect's data and constructs dictionary from it.
		Presumes that wordnet-affect is in child folder named, surprisingly,
		'wordnet-affect'.
		
		Returns dictionary from the data, where key is word from wordnet-affect 
		and value is list [id, tag, specific category, parent category]
	'''
	f = open('./wordnet-affect/id-syns-list.txt')
	a_words = {}
	
	for l in f.readlines():
		t = l.split()
		id = t[0]
		ws = t[1:]
		for w in ws:
			a_words[w] = [id]
			tag, categ = find_categ(id)
			a_words[w].append(tag)
			a_words[w].append(categ)
			a_words[w].append(find_parent(categ))
	
	f.close()		
	return a_words

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
			w = w.replace('_', ' ')
			s_words[w] = tag
			try:
				s_words[tag].append(w)
			except KeyError:
				s_words[tag] = [w]
				
#	for k,v in s_words.items():
#		print k, [w for w in v]
		
	return s_words
		

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
		print word, levenshtains[0]
		return levenshtains[0][0]
	else:
		return word
				
			



if __name__ == "__main__":
	'''
	if len(sys.argv) > 3 or len(sys.argv) < 2:
		print "Usage: python" + sys.argv[0] + " [v] <file path to raw text file (txt)>"
		print "v - optional argument for verbose output format."
		print "Remember to have wordnet-affect in same named subfolder and nltk"
		print "installed."
		sys.exit(0)
		
	docpath = ""	
	if len(sys.argv) == 2: 
		docpath = sys.argv[1]
	else:
		docpath = sys.argv[2]
		VERBOSE = True
	'''
	docpath = "./data/emmy.txt"
		
	f = open(docpath, 'r')
	raw = f.read()
	words = nltk.word_tokenize(raw)
	print
	
	# Position tag the words in document to decide which tag should be searched 
	# from to replace the word.
	print "Position tagging the document's words. This might take a while...",
	tagged_words = nltk.pos_tag(nltk.word_tokenize(raw))
	print "done."
	
	# dictionary of sexuality-wordnet's words. 
	print "Reading wordnet-sexuality's data...",
	s_words = read_wordnet_sexuality("./sexuality.txt")
	print "done."
	
	print "Replacing words in document...",
	altered_doc = replace_document_words(words, tagged_words, s_words)
	"done."
	
	# Print the altered document
	story = ""
	for w in altered_doc:
		story = story + " " + w
		
	print story






