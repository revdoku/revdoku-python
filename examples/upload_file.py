import os
import sys

from revdoku import Revdoku

bucket_id = os.getenv("REVDOKU_BUCKET_ID")
if not bucket_id or len(sys.argv) < 2:
    raise SystemExit("Set REVDOKU_BUCKET_ID and pass a local file path")
local_path = sys.argv[1]
with open(local_path, "rb") as file:
    content = file.read()
with Revdoku(account_id=os.getenv("REVDOKU_ACCOUNT_ID") or None) as client:
    bucket = client.get_bucket(bucket_id).data.bucket
    result = client.upload_file(
        bucket_id,
        sys.argv[2] if len(sys.argv) > 2 else os.path.basename(local_path),
        content,
        expected_bucket_version=bucket.version_id,  # Rejects the save after a concurrent change.
    )
    print(result.data.file.id, result.data.file.path)
