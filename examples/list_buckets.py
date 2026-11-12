import os

from revdoku import Revdoku

# Reads REVDOKU_API_KEY. REVDOKU_ACCOUNT_ID is optional.
with Revdoku(account_id=os.getenv("REVDOKU_ACCOUNT_ID") or None) as client:
    cursor = None
    seen = set()
    while True:
        page = client.list_buckets(status="active", limit=100, cursor=cursor).data
        for bucket in page.buckets:
            print(bucket.id, bucket.email.address if bucket.email and bucket.email.address else bucket.id)
        if not page.pagination.has_more:
            break
        cursor = page.pagination.next_cursor
        if not cursor or cursor in seen:
            raise RuntimeError("Bucket pagination did not advance")
        seen.add(cursor)
