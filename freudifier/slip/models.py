from django.db import models
from django.core import serializers
import logging
import traceback
import os
import shutil


logger = logging.getLogger('Slipper.slip')
POS = {}

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
		return [o['word'] for o in Noun.objects.exclude(word = '').values('word')]
	def NNS(self):
		return [o['plural'] for o in  Noun.objects.exclude(plural = '').values('plural')]
	def JJ(self):
		return [o['word'] for o in Adjective.objects.exclude(word = '').values('word')]
	def JJR(self):
		return [o['comparative'] for o in Adjective.objects.exclude(comparative = '').values('comparative')]
	def JJS(self):
		return [o['superlative'] for o in Adjective.objects.exclude(superlative = '').values('superlative')]
	def RB(self):
		return [o['word'] for o in Adverb.objects.exclude(word = '').values('word')]
	def RBR(self):
		return [o['comparative'] for o in Adverb.objects.exclude(comparative = '').values('comparative')] 
	def RBS(self):
		return [o['superlative'] for o in Adverb.objects.exclude(superlative = '').values('superlative')]
	def VB(self):
		return [o['word'] for o in Verb.objects.exclude(word = '').values('word')]
	def VBD(self):
		return [o['past_tense'] for o in Verb.objects.exclude(past_tense = '').values('past_tense')]
	def VBG(self):
		return [o['present_participle'] for o in Verb.objects.exclude(present_participle = '').values('present_participle')]
	def VBN(self):
		return [o['past_participle'] for o in Verb.objects.exclude(past_participle = '').values('past_participle')]
	def VBP(self):
		return [o['non_third_person_singular'] for o in Verb.objects.exclude(non_third_person_singular = '').values('non_third_person_singular')]
	def VBZ(self):
		return [o['third_person_singular'] for o in Verb.objects.exclude(third_person_singular = '').values('third_person_singular')]
	
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
	''' Just a wrapper for POSManager '''
	# Managed for easy POS retrieving.
	posmanager = POSManager()

'''
	True word categories and their words. 
	
	This is now a stupid work around since inheriting Word-model for all the 
	different part of speeches' meant some quite unexpected results with 
	POSManager. 
	
	TODO: Refactor me
	
	Fields:
	approved: 	is the latest version of the word approved by staff. This should
				be False if word was altered by user from the web site and true
				if the word was altered by staff member.
	category:	"Semantic" category of the word. This defaults to 'sexuality'
				which is the only category at the moment.
	word:		Base form of the word, ie. singular for noun, present tense for
				verb
	<other>:	These are distinct to the part of speech. 
'''
class Noun(models.Model):
	''' 
		Database model for nouns. Does not distinguish between proper and normal
		nouns. Probably there shouldn't be any proper nouns in the database 
		anyway.
	'''
	approved = models.BooleanField(default = False)
	category = models.CharField(default = 'sexuality', max_length = 100)
	word = models.CharField(max_length = 100, unique = True) # NN, NNP
	plural = models.CharField(blank = True, max_length = 100, default = '') # NNS, NNPS
	
	def save(self, *args, **kwargs):
		''' Override save to automatically update utils.POS '''
		super(Noun, self).save(*args, **kwargs)
		obj = self.objects.all()
		POS['NN'] = [o['word'] for o in obj]
		POS['NNS'] = [o['plural'] for o in obj if o['plural'] != '']
		POS['NNP'] = Word.POS['NN']
		POS['NNPS'] = Word.POS['NNS']
	
	class Meta:
		ordering = ['word']	
	
	
class Adjective(models.Model):
	''' Database model for adjectives. '''
	approved = models.BooleanField(default = False)
	category = models.CharField(default = 'sexuality', max_length = 100)
	word = models.CharField(max_length = 100, unique = True) # JJ
	comparative = models.CharField(blank = True, max_length = 100, default = '') #JJR
	superlative = models.CharField(blank = True, max_length = 100, default = '') #JJS
	
	def save(self, *args, **kwargs):
		''' Override save to automatically update utils.POS '''
		super(Adjective, self).save(*args, **kwargs)
		obj = self.objects.all()
		POS['JJ'] = [o['word'] for o in obj]
		POS['JJR'] = [o['comparative'] for o in obj if o['comparative'] != '']
		POS['JJS'] = [o['superlative'] for o in obj if o['superlative'] != '']
	
	class Meta:
		ordering = ['word']
		
	
class Adverb(models.Model):
	''' Database model for adverbs. '''
	approved = models.BooleanField(default = False)
	category = models.CharField(default = 'sexuality', max_length = 100)
	word = models.CharField(max_length = 100, unique = True) # RB
	comparative = models.CharField(blank = True, max_length = 100, default = '') # RBR
	superlative = models.CharField(blank = True, max_length = 100, default = '') # RBS
	
	def save(self, *args, **kwargs):
		''' Override save to automatically update utils.POS '''
		super(Adverb, self).save(*args, **kwargs)
		obj = self.objects.all()
		POS['RR'] = [o['word'] for o in obj.values('word')]
		POS['RBR'] = [o['comparative'] for o in obj if o['comparative'] != '']
		POS['RBS'] = [o['superlative'] for o in obj if o['superlative'] != '']
	
	class Meta:
		ordering = ['word']
			
	
class Verb(models.Model):
	''' Database model for verbs. '''
	approved = models.BooleanField(default = False)
	category = models.CharField(default = 'sexuality', max_length = 100)
	word = models.CharField(max_length = 100, unique = True) # VB
	past_tense = models.CharField(blank = True, max_length = 100, default = '') # VBD
	past_participle = models.CharField(blank = True, max_length = 100, default = '')  # VBN
	present_participle = models.CharField(blank = True, max_length = 100, default = '') # VBG, gerund
	third_person_singular = models.CharField(blank = True, max_length = 100, default = '') # VBZ
	non_third_person_singular = models.CharField(blank = True, max_length = 100, default = '') # VBP
	
	def save(self, *args, **kwargs):
		''' Override save to automatically update utils.POS '''
		super(Verb, self).save(*args, **kwargs)
		obj = self.objects.all()
		POS['VB'] = [o['word'] for o in obj.values('word')]
		POS['VBD'] = [o['past_tense'] for o in obj if o['past_tense'] != '']
		POS['VBN'] = [o['past_participle'] for o in obj if o['past_participle'] != '']
		POS['VBG'] = [o['present_participle'] for o in obj if o['present_participle'] != '']
		POS['VBZ'] = [o['third_person_singular'] for o in obj if o['third_person_singular'] != '']
		POS['VBP'] = [o['non_third_person_singular'] for o in obj if o['non_third_person_singular'] != '']


	
	class Meta:
		ordering = ['word']
	
POS = Word.posmanager.all_pos()	
