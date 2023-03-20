from rest_framework import serializers

class ExtraWebsiteSerializer(serializers.Serializer):
    html_content = serializers.CharField(required=True)    
    css = serializers.CharField(required=True)  
    page_id = serializers.CharField(required=True)  
    name = serializers.CharField(required=True)  

class SaveWebsiteSerializer(serializers.Serializer):
    html_content = serializers.CharField(required=True)    
    css = serializers.CharField(required=True)    
    template_id = serializers.IntegerField(required=False)    
    website_id = serializers.UUIDField(required=False) 
    extra_pages = ExtraWebsiteSerializer(many=True,required=False)
