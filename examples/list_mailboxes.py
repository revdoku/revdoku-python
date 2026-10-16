import os

from revdoku import Revdoku

# Reads REVDOKU_API_KEY. REVDOKU_ACCOUNT_ID is optional.
with Revdoku(account_id=os.getenv("REVDOKU_ACCOUNT_ID") or None) as client:
    cursor = None
    seen = set()
    while True:
        page = client.list_mailboxes(status="active", limit=100, cursor=cursor).data
        for mailbox in page.mailboxes:
            print(mailbox.id, mailbox.email.address if mailbox.email and mailbox.email.address else mailbox.id)
        if not page.pagination.has_more:
            break
        cursor = page.pagination.next_cursor
        if not cursor or cursor in seen:
            raise RuntimeError("Mailbox pagination did not advance")
        seen.add(cursor)
