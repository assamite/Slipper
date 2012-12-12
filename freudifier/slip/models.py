from django.db import models
from django.core import serializers
import logging
import traceback
import os
import shutil

logger = logging.getLogger('Slipper.slip')


class Tag(models.Model):
	'''
		Database model for part of speech tags. We are currently using Penn 
		Treebank tags:
		http://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
	'''
	TAGS = (
		('NN', 'noun'), 
		('NNS', 'noun, plural'), 
		('NNP', 'proper noun'), 
		('NNPS', 'proper noun, plural'), 		
		('JJ', 'adjective'), 
		('JJR', 'adjective, comparative'),
		('JJS', 'adjective, superlative'),
		('RB', 'adverb'),
		('RBR', 'adverb, comparative'),
		('RBS', 'adverb, superlative'),
		('VB', 'verb'),
		('VBD', 'verb, past tense'),
		('VBG', 'verb, gerund or present participle'),
		('VBN', 'verb, past participle'),
		('VBP', 'verb, non-third person singular present'),
		('VBZ', 'verb, third person singular present')
	)
	
	tag = models.CharField(choices = TAGS, max_length = 10)
	short_desc = models.CharField(max_length = 40, default = "")
	long_desc = models.CharField(blank = True, max_length = 1000)
	
	
class POSManager(models.Manager):
	'''
		Part of speech manager which has method for all the POS-tags in TAGS.
	'''
	def NN(self):
		return Noun.objects.exclude(word = '').values('word')
	def NNS(self):
		return Noun.objects.exclude(plural = '').values('plural')
	def JJ(self):
		return Adjective.objects.exclude(word = '').values('word')
	def JJR(self):
		return Adjective.objects.exclude(comparative = '').values('comparative')
	def JJS(self):
		return Adjective.objects.exclude(superlative = '').values('superlative')
	def RB(self):
		return Adverb.objects.exclude(word = '').values('word')
	def RBR(self):
		return Adverb.objects.exclude(comparative = '').values('comparative')
	def RBS(self):
		return Adverb.objects.exclude(superlative = '').values('superlative')
	def VB(self):
		return Verb.objects.exclude(word = '').values('word')
	def VBD(self):
		return Verb.objects.exclude(past_tense = '').values('past_tense')
	def VBG(self):
		return Verb.objects.exclude(present_participle = '').values('present_participle')
	def VBN(self):
		return Verb.objects.exclude(past_participle = '').values('past_participle')
	def VBP(self):
		return Verb.objects.exclude(non_third_person_singular = '').values('non_third_person_singular')
	def VBZ(self):
		return Verb.objects.exclude(third_person_singular = '').values('third_person_singular')
	
	def all_pos(self):
		'''
			Return all the POS from the database as a dictionary with Penn 
			Treebank tag as key and word in right form as value. Proper nouns
			use same words as normal nouns.
		'''
		# TODO: change this to use only 4 queries.
		POS = {}
		POS['NN'] = self.NN() 
		POS['NNS'] = self.NNS() 
		POS['NNP'] = POS['NN']
		POS['NNPS'] = POS['NNS']
		POS['JJ'] = self.JJ() 
		POS['JJR'] = self.JJR() 
		POS['JJS'] = self.JJS() 
		POS['RB'] = self.RB() 
		POS['RBR'] = self.RBR() 
		POS['RBS'] = self.RBS()
		POS['VB'] = self.VB() 
		POS['VBD'] = self.VBD() 
		POS['VBG'] = self.VBG() 
		POS['VBN'] = self.VBN() 
		POS['VBP'] = self.VBP() 
		POS['VBZ'] = self.VBZ()  
		return POS
	
	def serialize_words(self, file_format = 'json', filepath = ''):
		'''
			Serialize all words in file format and write them to filepath.
			(mostly for backupping initial data)
			
			Parameters:
			file_format: 	serializing format: 'xml', 'json' (default) or 'yaml'
			filepath:		filepath to write, defaults to 'word_dump.<format>'
		'''
		if file_format not in ['xml', 'json', 'yaml']:
			logger.info("Tried to dump database contents in wrong format %s" % file_format)
			return
			
		if not isinstance(filepath, str) or filepath == '':
			filepath = 'freudifier_'
		
		#if os.path.exists(filepath):	# just in case of major FUU..
		#	shutil.move(filepath, filepath + '.bk')
		
		serializer = serializers.get_serializer(file_format)
		Serializer = serializer()
		f = ''
		try:
			out = open(filepath+'noun.'+file_format, 'w')
			Serializer.serialize(Noun.objects.all(), stream = out)
			out.close()
			out = open(filepath+'adjective.'+file_format, 'w')
			Serializer.serialize(Adjective.objects.all(), stream = out)
			out.close()
			out = open(filepath+'adverb.'+file_format, 'w')
			Serializer.serialize(Adverb.objects.all(), stream = out)
			out.close()
			out = open(filepath+'verb.'+file_format, 'w')
			Serializer.serialize(Verb.objects.all(), stream = out)
			out.close()
		except:
			logger.error("Could not open file %s for serializing and dumping the database contents" % filepath)
			logger.error("Error stack \n %s" % traceback.format_exc())
			return
		
	
class Word(models.Model):
	''' Parent class for all the different word types' models. '''
	# Managed for easy POS retrieving.
	pos = POSManager()

class Noun(Word):
	''' Database model for nouns. '''
	# Has this word entry been approved by the staff.
	approved = models.BooleanField(default = False)
	#  Word's standard form, ie. singular for nouns and present tense for verbs.
	word = models.CharField(max_length = 100)
	category = models.CharField(default = 'sexuality', max_length = 100)
	plural = models.CharField(blank = True, max_length = 100, default = '')
	
	
class Adjective(Word):
	''' Database model for adjectives. '''
	# Has this word entry been approved by the staff.
	approved = models.BooleanField(default = False)
	#  Word's standard form, ie. singular for nouns and present tense for verbs.
	word = models.CharField(max_length = 100)
	category = models.CharField(default = 'sexuality', max_length = 100)
	comparative = models.CharField(blank = True, max_length = 100, default = '')
	superlative = models.CharField(blank = True, max_length = 100, default = '')
	
	
class Adverb(Word):
	''' Database model for adverbs. '''
	# Has this word entry been approved by the staff.
	approved = models.BooleanField(default = False)
	category = models.CharField(default = 'sexuality', max_length = 100)
	#  Word's standard form, ie. singular for nouns and present tense for verbs.
	word = models.CharField(max_length = 100)
	comparative = models.CharField(blank = True, max_length = 100, default = '')
	superlative = models.CharField(blank = True, max_length = 100, default = '')
	
	
class Verb(Word):
	''' Database model for verbs. '''
	# Has this word entry been approved by the staff.
	approved = models.BooleanField(default = False)
	category = models.CharField(default = 'sexuality', max_length = 100)
	#  Word's standard form, ie. singular for nouns and present tense for verbs.
	word = models.CharField(max_length = 100)
	past_tense = models.CharField(blank = True, max_length = 100, default = '')
	past_participle = models.CharField(blank = True, max_length = 100, default = '')
	present_participle = models.CharField(blank = True, max_length = 100, default = '')
	third_person_singular = models.CharField(blank = True, max_length = 100, default = '')
	non_third_person_singular = models.CharField(blank = True, max_length = 100, default = '')
	
