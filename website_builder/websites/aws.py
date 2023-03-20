import boto3
import json
from botocore.exceptions import ClientError
from django.conf import settings

class S3:
    def __init__(self, region,bucket_name,*args, **kwargs):
        self.region = region
        self.bucket_name = bucket_name
        self.client = self.create_s3_client()

    def create_s3_client(self):
        client = boto3.client('s3',
            aws_access_key_id=settings.AWS_HOST_ACCESS_KEY_ID,
            aws_secret_access_key= settings.AWS_HOST_SECRET_ACCESS_KEY,
            region_name=self.region
        )
        return client

    def delete_bucket(self):
        try:
           response = self.client.delete_bucket(
                Bucket=self.bucket_name,
            )
        except ClientError as e:
            print(e)
            return False
        return True

    def get_bucket(self):
        try:
            response = self.client.get_bucket_website(
                Bucket=self.bucket_name,
                )
        except ClientError as e:
            print(e)
            return False
        return True

    def create_bucket(self):
        # Create bucket
        try:
            location = {'LocationConstraint': self.region}
            response = self.client.create_bucket(
                Bucket=self.bucket_name,
                CreateBucketConfiguration=location
                )
            return True
        except ClientError as e:
            print(e)
            return False

    def create_website_config(self):
        website_configuration = {
            'ErrorDocument': {'Key': 'error.html'},
            'IndexDocument': {'Suffix': 'index.html'},
        }

        try:
            response = self.client.put_bucket_website(
                Bucket=self.bucket_name,
                WebsiteConfiguration=website_configuration
                )
        except ClientError as e:
            print(e)
            return False
        return True

    def set_bucket_policy(self):
        policy = '{"Version": "2012-10-17","Statement": [{"Sid": "PublicReadGetObject","Effect": "Allow","Principal": "*","Action": "s3:GetObject","Resource": "arn:aws:s3:::%s/*"}]}' % self.bucket_name

        try:
            response = self.client.put_bucket_policy(
                Bucket=self.bucket_name,
                Policy=policy
            )
        except ClientError as e:
            print(e)
            return False
        return True

    def upload_file(self,file_name, object_name=None):
        try:
            response = self.client.upload_file(
                file_name,
                self.bucket_name,
                object_name,
                ExtraArgs={'ContentType': "text/html", 'ACL': "public-read"}
                )
        except ClientError as e:
            logging.error(e)
            return False
        return True

class Acm:
    def __init__(self,*args, **kwargs):
        self.client = self.create_amc_client()

    def create_amc_client(self):
        client = boto3.client('acm',
            aws_access_key_id=settings.AWS_HOST_ACCESS_KEY_ID,
            aws_secret_access_key= settings.AWS_HOST_SECRET_ACCESS_KEY,
            region_name="us-east-1"
        )
        return client

    def request_certificate(self,domain):
        try:
            response = self.client.request_certificate(
                DomainName=domain,
                ValidationMethod='DNS',
                SubjectAlternativeNames=[
                        f"*.{domain}"
                    ]
                )
        except ClientError as e:
            print(e)
            return False
        return response

    def delete_certificate(self,arn):
        try:
            response = self.client.delete_certificate(
                  CertificateArn=arn
                )
        except ClientError as e:
            print(e)
            return False
        return response

    def get_domain_validation_records(self, certificate_arn):
        """ Return the domain validation records from the describe_certificate
            call for our certificate
        """
        certificate_metadata = self.client.describe_certificate(
            CertificateArn=certificate_arn)
        return certificate_metadata.get('Certificate', {}).get(
            'DomainValidationOptions', [])

    def get_certificate_status(self, certificate_arn):
        return self.client.describe_certificate(CertificateArn=certificate_arn)['Certificate']['Status']

class CloudFront:
    def __init__(self,*args, **kwargs):
        self.client = self.create_cf_client()

    def create_cf_client(self):
        client = boto3.client('cloudfront',
            aws_access_key_id=settings.AWS_HOST_ACCESS_KEY_ID,
            aws_secret_access_key= settings.AWS_HOST_SECRET_ACCESS_KEY,
            region_name="eu-central-1"
        )
        return client

    def get_distribution_config(self,Id):
        try:
            response = self.client.get_distribution_config(
                Id=Id,
            )
        except ClientError as e:
            print(e)
            return False
        return response

    def create_distribution(self,hosted_website):
        website = hosted_website.website
        origin_url = hosted_website.s3_url.replace("http://","")
        print(origin_url)
        origin_id = f"S3-Website-{origin_url}"
        config = {
               'CallerReference': str(website.private_uuid),
                'Aliases': {
                    'Quantity': 2,
                    'Items': [
                        f'*.{website.domain_name}',
                        website.domain_name
                    ]
                },
                'Comment':'',
                'Enabled':True,
                'Origins': {
                    'Quantity': 1,
                    'Items': [
                        {
                            'Id': origin_id,
                            'DomainName': origin_url,
                            'CustomOriginConfig': {
                                'HTTPPort': 80,
                                'HTTPSPort': 443,
                                'OriginProtocolPolicy': 'http-only',
                                'OriginSslProtocols': {
                                    'Quantity': 4,
                                    'Items': [
                                        'SSLv3','TLSv1','TLSv1.1','TLSv1.2',
                                    ]
                                }
                            },
                        },

                    ]
                },
                'DefaultCacheBehavior': {
                    'TargetOriginId':origin_id,
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'ForwardedValues': {
                        'QueryString': False,
                        'Cookies': {
                            'Forward': 'all',
                        }
                    },
                    'MinTTL': 5,
                },
                'ViewerCertificate': {
                    'CloudFrontDefaultCertificate': False,
                    'ACMCertificateArn': hosted_website.certificate_arn,
                    'SSLSupportMethod': 'sni-only'
                },
        }
        try:
            response = self.client.create_distribution(
                DistributionConfig=config
            )

        except ClientError as e:
            print(e)
            return False
        return response

    def delete_distribution(self,Id,IfMatch):
        try:
            response = self.client.delete_distribution(
                Id=Id,
                IfMatch=IfMatch
            )
        except ClientError as e:
            print(e)
            return False
        return response

    def disable_distribution(self,Id):
        dist_response = self.get_distribution_config(Id)
        if dist_response:
            config = dist_response['DistributionConfig']
            IfMatch = dist_response['ETag']
        else:
            return False

        config['Enabled'] = False

        try:
            response = self.client.update_distribution(
                DistributionConfig=config,
                Id=Id,
                IfMatch=IfMatch
            )
        except ClientError as e:
            print(e)
            return False
        return response

    def enable_distribution(self,Id):
        dist_response = self.get_distribution_config(Id)
        if dist_response:
            config = dist_response['DistributionConfig']
            IfMatch = dist_response['ETag']
        else:
            return False

        config['Enabled'] = True

        try:
            response = self.client.update_distribution(
                DistributionConfig=config,
                Id=Id,
                IfMatch=IfMatch
            )
        except ClientError as e:
            print(e)
            return False
        return response
