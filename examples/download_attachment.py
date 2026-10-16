import os

from revdoku import Revdoku

names = ("REVDOKU_MAILBOX_ID", "REVDOKU_EMAIL_ID", "REVDOKU_ATTACHMENT_ID", "REVDOKU_DOWNLOAD_PATH")
mailbox_id, email_id, attachment_id, output = (os.getenv(name) for name in names)
if not (mailbox_id and email_id and attachment_id and output):
    raise SystemExit("Set " + ", ".join(names))
with Revdoku(account_id=os.getenv("REVDOKU_ACCOUNT_ID") or None) as client:
    content = client.download_attachment(mailbox_id, email_id, attachment_id)
with open(output, "xb") as file:  # Never overwrites an existing file.
    file.write(content)
print(output)
