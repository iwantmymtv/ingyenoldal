from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

from website_builder.builder.models import Template,Block
from website_builder.builder.serializers import (
    TemplateSerializer,
    WebsiteSerializer,
    BlockSerializer,
    UploadedAssetListSerializer
)
from website_builder.builder.utils import is_valid_uuid
from website_builder.websites.models import Website,UploadedAsset

class GetTemplate(APIView):

    def get(self, request, id):
        user = request.user
        website = None
        print('idddd:   ', id)
        if is_valid_uuid(id):
            print('idddd:   ', id)
            website = get_object_or_404(Website,uid=id,user=user)
            template = website.template
        else:
            template = get_object_or_404(Template,id=id,is_editable=True)
        
        blocks = Block.objects.filter(style__isnull=True)

        #add style related block
        for b in template.styles.all():
            blocks |= b.blocks.all()
        
        template_serializer = TemplateSerializer(template)

        ctx = {
            'template': template_serializer.data,
            'blocks':[BlockSerializer(b).data for b in blocks]
        }
        if website:
            website_serialzer = WebsiteSerializer(website)
            ctx['website'] = website_serialzer.data

        return Response(ctx)

class GetUserUploadedAssets(APIView):

    def get(self, request):
        user = request.user
        assets = UploadedAsset.objects.filter(user=user)
        serilaizer = UploadedAssetListSerializer(assets,many=True)
        return Response(serilaizer.data)