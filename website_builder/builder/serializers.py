from rest_framework import serializers
from website_builder.builder.models import (
    Template,
    Style,
    Script,
    Block,
    BlockCategory,
    TemplateExtraPage    
)
from website_builder.websites.models import Website,UploadedAsset,WebsiteExtraPage

class UploadedAssetListSerializer(serializers.ModelSerializer):
    asset_thumbnail = serializers.ImageField(read_only=True)
    class Meta:
        model = UploadedAsset
        fields = ['asset','asset_thumbnail']

class UploadedAssetSerializer(serializers.Serializer):
    assets = serializers.ListField(
        source="assets[]",
        child=serializers.FileField()
    )
class StyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Style
        fields = '__all__'

class ScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Script
        fields = '__all__'

class TemplateExtraPageSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="page_id")
    styles = serializers.CharField(source="css")
    component = serializers.CharField(source="html_content")
    class Meta:
        model = TemplateExtraPage
        fields = ['id','name','styles','component']

class WebsiteExtraPageSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="page_id")
    styles = serializers.CharField(source="css")
    component = serializers.CharField(source="html_content")
    class Meta:
        model = WebsiteExtraPage
        fields = ['id','name','styles','component']

class TemplateSerializer(serializers.ModelSerializer):
    styles = StyleSerializer(many=True)
    scripts = ScriptSerializer(many=True)
    pages = TemplateExtraPageSerializer(many=True)
    class Meta:
        model = Template
        fields = ['id','styles','scripts','html_content','pages']

class WebsiteSerializer(serializers.ModelSerializer):
    pages = WebsiteExtraPageSerializer(many=True)
    class Meta:
        model = Website
        fields = ['id','uid','html_content','css','pages']

class BlockCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockCategory
        fields = ['name']



class BlockSerializer(serializers.ModelSerializer):
    category = BlockCategorySerializer()
    image_thumbnail = serializers.ImageField(read_only=True)
    class Meta:
        model = Block
        fields = ['uid','category','name','image_thumbnail','html_content','info_content']