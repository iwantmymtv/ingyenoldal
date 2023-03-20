from django.contrib import admin
from website_builder.builder.forms import (
    TemplateAdminForm,
    BlockAdminForm
)
from website_builder.builder.models import (
    TemplateCategory,
    Style,
    Script,
    Template,
    BlockCategory,
    AttributeType,
    BlockAttributes,
    Block,
    TemplateExtraPage
)

class PageInline(admin.StackedInline):
    model = TemplateExtraPage
    extra = 0

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    form = TemplateAdminForm
    prepopulated_fields = {'slug': ('name',), }
    list_filter = ['styles','category','is_premium','is_public']
    list_display = ['name','is_premium','is_public','is_editable']
    filter_horizontal = ["styles","scripts"]
    inlines = [PageInline]

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    form = BlockAdminForm
    list_display = ['name','category']
    list_filter = ['category','style','script']
    filter_horizontal = ["style","script",'attributes']

@admin.register(TemplateCategory)
class TemplateCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(BlockCategory)
class BlockCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Style)
class StyleAdmin(admin.ModelAdmin):
    pass

@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    pass

@admin.register(AttributeType)
class AttributeTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(BlockAttributes)
class BlockAttributesAdmin(admin.ModelAdmin):
    pass

