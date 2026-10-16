import os

from revdoku import Revdoku

mailbox_id = os.getenv("REVDOKU_MAILBOX_ID")
if not mailbox_id:
    raise SystemExit("Set REVDOKU_MAILBOX_ID")
with Revdoku(account_id=os.getenv("REVDOKU_ACCOUNT_ID") or None) as client:
    cursor = None
    seen = set()
    while True:
        page = client.list_files(mailbox_id, limit=100, cursor=cursor).data
        for file in page.files:
            print(file.to_json())
        if not page.pagination.has_more:
            break
        cursor = page.pagination.next_cursor
        if not cursor or cursor in seen:
            raise RuntimeError("File pagination did not advance")
        seen.add(cursor)
