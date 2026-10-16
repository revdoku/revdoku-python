import os
import sys

from revdoku import Revdoku

mailbox_id = os.getenv("REVDOKU_MAILBOX_ID")
if not mailbox_id or len(sys.argv) < 2:
    raise SystemExit("Set REVDOKU_MAILBOX_ID and pass a local file path")
local_path = sys.argv[1]
with open(local_path, "rb") as file:
    content = file.read()
with Revdoku(account_id=os.getenv("REVDOKU_ACCOUNT_ID") or None) as client:
    mailbox = client.get_mailbox(mailbox_id).data.mailbox
    result = client.upload_file(
        mailbox_id,
        sys.argv[2] if len(sys.argv) > 2 else os.path.basename(local_path),
        content,
        expected_mailbox_version=mailbox.version_id,  # Rejects the save after a concurrent change.
    )
    print(result.data.file.id, result.data.file.path)
