from modeltranslation.translator import register, TranslationOptions
from website_builder.subscriptions.models import Plan

@register(Plan)
class PlanTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

