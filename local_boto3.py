import boto3
boto3.set_stream_logger(name='botocore')

session = boto3.Session(profile_name='joe', region_name='us-east-1')
s3 = session.client('s3')

print(s3.list_buckets())
