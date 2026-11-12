import json
import os
import sys

from revdoku import Revdoku, RevdokuError

with Revdoku(account_id=os.getenv("REVDOKU_ACCOUNT_ID") or None) as client:
    try:
        result = client.create_bucket(
            username=os.getenv("REVDOKU_EMAIL_USERNAME") or None,
            domain=os.getenv("REVDOKU_EMAIL_DOMAIN") or None,
        )
    except RevdokuError as error:
        print(f"HTTP {error.status}: {error.code}", json.dumps(error.details), file=sys.stderr)
        if error.retry_after is not None:
            print(f"Retry after {error.retry_after} seconds", file=sys.stderr)
        # Never repeat a creation automatically: it may have succeeded.
        print("Creation was not confirmed. Check existing buckets before another creation attempt.", file=sys.stderr)
        sys.exit(1)
    except Exception:
        print("Creation response unavailable. Check existing buckets before another creation attempt.", file=sys.stderr)
        sys.exit(1)
    print(result.data.bucket.id, result.data.bucket.email.address if result.data.bucket.email else None)
