import os
from revdoku_api import ApiClient, Configuration, DefaultApi, CreateBucketRequest, CreateBucketRequestBucket

key = os.environ["REVDOKU_API_KEY"]
if not key:
    raise ValueError("Set REVDOKU_API_KEY")
with ApiClient(Configuration(access_token=key)) as client:
    result = DefaultApi(client).create_bucket(CreateBucketRequest(
        account_id=os.getenv("REVDOKU_ACCOUNT_ID") or None,
        bucket=CreateBucketRequestBucket(title="Example inbox"),
    ))
    print(result.data.bucket.id, result.data.bucket.email.address)
# A timeout or EMAIL_NOT_READY may leave a created bucket. Inspect it before retrying.
