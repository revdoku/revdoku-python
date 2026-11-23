import os

from revdoku import Revdoku

names = ("REVDOKU_PROJECT_ID", "REVDOKU_TICKET_ID", "REVDOKU_MESSAGE_ID", "REVDOKU_ATTACHMENT_ID", "REVDOKU_DOWNLOAD_PATH")
project_id, ticket_id, message_id, attachment_id, output = (os.getenv(name) for name in names)
if not (project_id and ticket_id and message_id and attachment_id and output):
    raise SystemExit("Set " + ", ".join(names))
with Revdoku(account_id=os.getenv("REVDOKU_ACCOUNT_ID") or None) as client:
    content = client.download_attachment(project_id, ticket_id, message_id, attachment_id)
with open(output, "xb") as file:  # Never overwrites an existing file.
    file.write(content)
print(output)
