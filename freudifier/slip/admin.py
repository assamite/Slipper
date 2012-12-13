from django.contrib import admin
from freudifier.slip.models import Noun, Adjective, Adverb, Verb

def mark_approved(modeladmin, request, queryset):
		queryset.update(approved = True)
	
mark_approved.short_description = "Mark select words as approved"


class NounAdmin(admin.ModelAdmin):
	list_display = ('approved', 'word', 'plural', 'category')
	search_fields = ('word')
	list_filter = ('approved', 'category')
	actions = [mark_approved]


class AdjectiveAdmin(admin.ModelAdmin):
	list_display = ('approved', 'word', 'comparative', 'superlative', 'category')
	search_fields = ('word')
	list_filter = ('approved', 'category')
	actions = [mark_approved]
	

class AdverbAdmin(admin.ModelAdmin):
	list_display = ('approved', 'word', 'comparative', 'superlative', 'category')  
	search_fields = ('word')
	list_filter = ('approved', 'category')
	actions = [mark_approved]


class VerbAdmin(admin.ModelAdmin):
	list_display = ('approved', 'word', 'past_tense', 'present_participle', 'category')
	search_fields = ('word')	
	list_filter = ('approved', 'category')
	actions = [mark_approved]


admin.site.register(Noun, NounAdmin)
admin.site.register(Adjective, AdjectiveAdmin)
admin.site.register(Adverb, AdverbAdmin)
admin.site.register(Verb, VerbAdmin)
