import requests
import boto3
import datetime
import hashlib
import hmac

# The whole process for making a raw AWS call
# https://docs.aws.amazon.com/IAM/latest/UserGuide/create-signed-request.html
# Example: S3 ListBuckets

REGION = 'us-east-1'
AWS_ACCESS_KEY_ID = 'YOUR_KEY_HERE'
AWS_SECRET_ACCESS_KEY = 'YOUR_SECRET_HERE'

utcnow = datetime.datetime.now(tz=datetime.timezone.utc)
x_amz_date = utcnow.strftime('%Y%m%dT%H%M%SZ')

# Step 1: create a canonical request
# NOTE: The x-amz-content-sha256 is the hex digest of the sha256 hash of an empty string
canonical_request = f'''
GET
/

host:s3.amazonaws.com
x-amz-content-sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
x-amz-date:{x_amz_date}

host;x-amz-content-sha256;x-amz-date
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
'''.strip()

# Step 2: Create a hash of the canonical request
canonical_hash = hashlib.sha256(canonical_request.encode('utf8')).hexdigest()

# print(canonical_hash)

# Step 3: Create a string to sign
current_date = utcnow.strftime('%Y%m%d')
print(current_date)
credential_scope = f'{current_date}/{REGION}/s3/aws4_request'
string_to_sign = f'''
AWS4-HMAC-SHA256
{x_amz_date}
{credential_scope}
{canonical_hash}
'''.strip()
print(string_to_sign)

# Step 4: Calculate the signature
def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def get_signature_key(key, date_stamp, region_name, service_name):
    k_date = sign(('AWS4' + key).encode('utf-8'), date_stamp)
    k_region = sign(k_date, region_name)
    k_service = sign(k_region, service_name)
    k_signing = sign(k_service, 'aws4_request')
    return k_signing

signing_key = get_signature_key(
    AWS_SECRET_ACCESS_KEY,
    current_date,
    REGION,
    's3'
)

signature = hmac.new(signing_key, string_to_sign.encode('utf8'), hashlib.sha256).hexdigest()

print(signature)

# Step 5: Add signature to request
# NOTE: Make the request, then?
authorization_header_value = f'AWS4-HMAC-SHA256 Credential={AWS_ACCESS_KEY_ID}/{credential_scope}, SignedHeaders=host;x-amz-content-sha256;x-amz-date, Signature={signature}'
res = requests.get(
    'https://s3.amazonaws.com',
    headers={
        'X-Amz-Date': x_amz_date,
        'X-Amz-Content-Sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        'Authorization': authorization_header_value,
    }
)

print(res.text)
