from django.db.models.signals import pre_delete
from django.dispatch import receiver
from website_builder.websites.aws import S3,Acm,CloudFront
from website_builder.websites.models import HostedWebsite

@receiver(pre_delete, sender=HostedWebsite)
def delete_aws_website(sender, instance, using, **kwargs):
    s3 = S3(instance.get_region(),instance.get_bucket_name())
    acm = Acm()
    cloudfront = CloudFront()
    #delete cloudfront
    cf_response = cloudfront.disable_distribution(instance.distribution_id)
    if cf_response:
        cloudfront.delete_distribution(instance.distribution_id,cf_response['ETag'])
    #will delete unused certificates
    acm.delete_certificate(instance.certificate_arn)

    #delete s3 bucket
    #s3.delete_bucket()
