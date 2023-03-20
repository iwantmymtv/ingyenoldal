from modeltranslation.translator import register, TranslationOptions
from website_builder.builder.models import Block,BlockCategory,Template,TemplateCategory

@register(Block)
class BlockTranslationOptions(TranslationOptions):
    fields = ('name', )

@register(BlockCategory)
class BlockCategoryTranslationOptions(TranslationOptions):
    fields = ('name', )

@register(Template)
class TemplateTranslationOptions(TranslationOptions):
    fields = ('name','description')

@register(TemplateCategory)
class TemplateCategoryTranslationOptions(TranslationOptions):
    fields = ('name','description')
