import json
import os
import sys
import time

from revdoku import Revdoku, RevdokuError

project_id = os.getenv("REVDOKU_PROJECT_ID")
if not project_id:
    raise SystemExit("Set REVDOKU_PROJECT_ID")


def read_message(client, ticket_id, message_id):
    """The AI filter checks a new message for up to about a minute. Until then, reading it
    returns 503 EMAIL_LABELING_PENDING with Retry-After."""
    for _ in range(12):
        try:
            return client.get_ticket_message(project_id, ticket_id, message_id).data.message
        except RevdokuError as error:
            if error.code != "EMAIL_LABELING_PENDING":
                raise
            time.sleep(error.retry_after or 5)
    return None


# A ticket is one conversation: an email or a message left on your docs site.
with Revdoku(account_id=os.getenv("REVDOKU_ACCOUNT_ID") or None) as client:
    cursor = None
    seen = set()
    while True:
        page = client.list_tickets(project_id, limit=100, status="open", cursor=cursor).data
        for ticket in page.tickets:
            # A page holds 20 messages by default: follow the cursor until has_more is false.
            message_cursor = None
            seen_messages = set()
            while True:
                thread = client.list_ticket_messages(project_id, ticket.id, cursor=message_cursor).data
                for summary in thread.messages:
                    if summary.direction != "received":
                        continue
                    if any(label.name == "Junk" for label in summary.labels):
                        continue  # Revdoku withholds junk content.
                    message = read_message(client, ticket.id, summary.id)
                    if message is None:
                        print(f"{summary.id} is still being checked. Run again later.", file=sys.stderr)
                        continue
                    print(json.dumps({"ticket_id": ticket.id, "number": ticket.number, "channel": ticket.channel,
                                      "id": message.id, "subject": message.subject,
                                      "body_status": message.body_status, "body_text": message.body_text,
                                      "attachments": [item.to_dict() for item in message.attachments or []]}, ensure_ascii=False))
                if not thread.pagination.has_more:
                    break
                message_cursor = thread.pagination.next_cursor
                if not message_cursor or message_cursor in seen_messages:
                    raise RuntimeError("Message pagination did not advance")
                seen_messages.add(message_cursor)
        if not page.pagination.has_more:
            break
        cursor = page.pagination.next_cursor
        if not cursor or cursor in seen:
            raise RuntimeError("Ticket pagination did not advance")
        seen.add(cursor)
# Reading does not change the shared read status or the ticket status.
