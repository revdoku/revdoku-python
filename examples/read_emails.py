import json
import os
import sys
import time

from revdoku import Revdoku, RevdokuError

mailbox_id = os.getenv("REVDOKU_MAILBOX_ID")
if not mailbox_id:
    raise SystemExit("Set REVDOKU_MAILBOX_ID")


def read_email(client, email_id):
    """AI labels check a new email for up to about a minute. Until then, reading it
    returns 503 EMAIL_LABELING_PENDING with Retry-After."""
    for _ in range(12):
        try:
            return client.get_email(mailbox_id, email_id).data.email
        except RevdokuError as error:
            if error.code != "EMAIL_LABELING_PENDING":
                raise
            time.sleep(error.retry_after or 5)
    return None


with Revdoku(account_id=os.getenv("REVDOKU_ACCOUNT_ID") or None) as client:
    cursor = None
    seen = set()
    while True:
        page = client.list_emails(mailbox_id, limit=100, order="asc", read=False, cursor=cursor).data
        for summary in page.emails:
            if any(label.name == "Junk" for label in summary.labels):
                continue  # Revdoku withholds junk content.
            email = read_email(client, summary.id)
            if email is None:
                print(f"{summary.id} is still being labeled. Run again later.", file=sys.stderr)
                continue
            print(json.dumps({"id": email.id, "subject": email.subject,
                              "body_status": email.body_status, "body_text": email.body_text,
                              "attachments": [item.to_dict() for item in email.attachments]}, ensure_ascii=False))
        if not page.pagination.has_more:
            break
        cursor = page.pagination.next_cursor
        if not cursor or cursor in seen:
            raise RuntimeError("Email pagination did not advance")
        seen.add(cursor)
# Reading does not change the shared read status.
