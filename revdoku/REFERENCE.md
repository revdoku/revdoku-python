# Revdoku API reference for Python

Generated from the Revdoku OpenAPI. Web version with examples: https://revdoku.com/api/reference.md

```sh
pip install revdoku
```

Python 3.10 or later.

```python
from revdoku import Revdoku, RevdokuError

client = Revdoku()  # reads REVDOKU_API_KEY
response = client.list_mailboxes()
print(response.data.mailboxes)
```

- Every call returns the API envelope. Read results from `.data`.
- Field names are the JSON names in snake_case.
- API error responses raise `RevdokuError` with `status`, `code`, `message`, `details`, `request_id` and `retry_after` (seconds). Network, timeout and TLS failures raise urllib3 exceptions, such as `urllib3.exceptions.SSLError`.
- Options: `Revdoku(api_key=None, account_id=None, base_url=None, timeout=30.0)`. `base_url` is the origin without `/v1`.
- `client.api` has every operation below. Mutations are never retried automatically.

## Helpers

- `client.list_mailboxes(**filters)`: List mailboxes.
- `client.get_mailbox(mailbox_id, **options)`: Read a mailbox.
- `client.create_mailbox(username=None, domain=None, title=None, account_id=None, *, description=None, metadata=None, **options)`: Create a mailbox. Never retry automatically after an uncertain result.
- `client.list_emails(mailbox_id, **filters)`: List emails. Poll with the saved pagination.next_cursor.
- `client.get_email(mailbox_id, email_id, **options)`: Read an email.
- `client.list_files(mailbox_id, **filters)`: List files.
- `client.get_attachment_download(mailbox_id, email_id, attachment_id, **options)`: Get a temporary download link for an attachment.
- `client.download_attachment(mailbox_id, email_id, attachment_id, max_bytes=64 * 1024 * 1024, **options)`: Download attachment bytes.
- `client.upload_file(mailbox_id, path, content, content_type=None, account_id=None, expected_mailbox_version=None, **options)`: Upload bytes or text and save a file version. `_request_timeout` also limits the storage transfer.

## Authentication

Operations that need no API key run before you have one. They use the generated `DefaultApi` class instead of `Revdoku`, so their errors are `ApiException`, not `RevdokuError`.

### Email a sign-in code

`POST /v1/agent_auth/request_code` · [web reference](https://revdoku.com/api/reference/authentication.md#email-a-sign-in-code)

`DefaultApi().request_sign_in_code(request_sign_in_code_request)`

Needs no API key. Sends a six-digit code to an existing account email. The response is the same for every address, so it never reveals whether an account exists. Create new accounts in the browser at https://app.revdoku.com/users/sign_up.

Body `request_sign_in_code_request` (`RequestSignInCodeRequest`): `email` (string (email), required), `account_id` (string), `reason` (string or null).

### Exchange a sign-in code for an API key

`POST /v1/agent_auth/verify_code` · [web reference](https://revdoku.com/api/reference/authentication.md#exchange-a-sign-in-code-for-an-api-key)

`DefaultApi().verify_sign_in_code(verify_sign_in_code_request)`

Needs no API key. Creates an AI agent connection for an account owner or administrator. Accounts with two-factor authentication must use browser sign-in.

Body `verify_sign_in_code_request` (`VerifySignInCodeRequest`): `email` (string (email), required), `code` (string, required), `label` (string), `permission_scope` (string: `mailbox_read`, `mailbox_write`, `mailbox_admin`), `mailbox_access` (string: `all`, `selected`), `mailbox_ids` (array of string), `mailbox_permissions` (object), `account_id` (string), `reason` (string or null).

### Exchange a one-time dashboard connection code for an API key

`POST /v1/agent_auth/exchange_grant` · [web reference](https://revdoku.com/api/reference/authentication.md#exchange-a-one-time-dashboard-connection-code-for-an-api-key)

`DefaultApi().exchange_connection_grant(exchange_connection_grant_request)`

Needs no API key. The dashboard creates the one-time code when a signed-in administrator copies a connection prompt.

Body `exchange_connection_grant_request` (`ExchangeConnectionGrantRequest`): `grant_token` (string, required), `label` (string), `account_id` (string), `reason` (string or null).

### Create a dashboard link for the user

`POST /v1/agent_auth/browser_login_link` · [web reference](https://revdoku.com/api/reference/authentication.md#create-a-dashboard-link-for-the-user)

`client.api.create_browser_link(create_browser_link_request)`

Returns a dashboard URL for a path such as /mailboxes. The user signs in normally; the link grants no access.

Body `create_browser_link_request` (`CreateBrowserLinkRequest`): `redirect_path` (string), `account_id` (string), `reason` (string or null).

## Accounts

### Read the connection and selected account

`GET /v1/status` · [web reference](https://revdoku.com/api/reference/accounts.md#read-the-connection-and-selected-account)

`client.api.get_status()`

Works with every API key, including mailbox-scoped keys. Read quotas with GET /v1/account/limits.

Parameters: `account_id` (string), `reason` (string or null).

### List accounts granted to this credential

`GET /v1/accounts` · [web reference](https://revdoku.com/api/reference/accounts.md#list-accounts-granted-to-this-credential)

`client.api.list_accounts()`

Works with every API key. Lists the account of this credential and the client accounts that an agency owner granted to it. Send an id from this list as account_id to act in that account.

Parameters: `limit` (integer), `cursor` (string).

### Create a client account

`POST /v1/accounts` · [web reference](https://revdoku.com/api/reference/accounts.md#create-a-client-account)

`client.api.create_client_account(create_client_account_request)`

Requires an agency owner credential with client-account access. The credential default does not change; send the new account_id on later requests.

Body `create_client_account_request` (`CreateClientAccountRequest`): `name` (string, required), `client_name` (string), `account_id` (string), `reason` (string or null).

### Read one granted account

`GET /v1/accounts/{account_id}` · [web reference](https://revdoku.com/api/reference/accounts.md#read-one-granted-account)

`client.api.get_account(account_id)`

Works with every API key. Returns the name, kind, region and status of one account that this credential can use, and the permissions of the credential in it. Other account IDs return 403.

Parameters: `account_id` (string, required).

### Read effective account limits

`GET /v1/account/limits` · [web reference](https://revdoku.com/api/reference/accounts.md#read-effective-account-limits)

`client.api.get_account_limits()`

Values come from the plan and account overrides. Zero means no allowance; null means no cap. Storage, mailbox and email traffic allowances are shared within a billing group.

Parameters: `account_id` (string).

## Mailboxes

### List mailboxes

`GET /v1/mailboxes` · [web reference](https://revdoku.com/api/reference/mailboxes.md#list-mailboxes)

`client.list_mailboxes()`. Full API: `client.api.list_mailboxes()`.

Lists active mailboxes by default, newest first. Counts and pages cover only mailboxes this credential can access. Reads no email content.

Parameters: `account_id` (string), `reason` (string or null), `status` (string: `active`, `archived`, `all`), `q` (string), `limit` (integer), `cursor` (string).

### Create a mailbox

`POST /v1/mailboxes` · [web reference](https://revdoku.com/api/reference/mailboxes.md#create-a-mailbox)

`client.create_mailbox(username=..., domain=..., title=...)`. Full API: `client.api.create_mailbox(create_mailbox_request)`.

Waits until the address can receive email. On revdokumail.com, email.username is a prefix with a permanent 4-character random suffix on every plan; a custom domain takes the exact name. If confirmation does not finish, EMAIL_NOT_READY returns the created mailbox_id in error.details: read that mailbox instead of creating another. The title defaults to email.username; a title that another active mailbox uses returns 409 MAILBOX_TITLE_TAKEN. Never retry a creation automatically.

Body `create_mailbox_request` (`CreateMailboxRequest`): `mailbox` (MailboxCreate), `account_id` (string), `reason` (string or null).

### Read a mailbox

`GET /v1/mailboxes/{mailbox_id}` · [web reference](https://revdoku.com/api/reference/mailboxes.md#read-a-mailbox)

`client.get_mailbox(mailbox_id)`. Full API: `client.api.get_mailbox(mailbox_id)`.

Reading never changes the mailbox. Read address settings, emails and files through their own endpoints.

Parameters: `mailbox_id` (string, required), `account_id` (string), `reason` (string or null).

### Update a mailbox title, description or metadata

`PATCH /v1/mailboxes/{mailbox_id}` · [web reference](https://revdoku.com/api/reference/mailboxes.md#update-a-mailbox-title-description-or-metadata)

`client.api.update_mailbox(mailbox_id, update_mailbox_request)`

metadata must be a JSON object. It replaces the stored object; {} clears it. Send expected_metadata_version from your last read; a stale value changes nothing and returns MAILBOX_METADATA_CONFLICT. Titles are unique among active mailboxes; a used title returns 409 MAILBOX_TITLE_TAKEN.

Parameters: `mailbox_id` (string, required).

Body `update_mailbox_request` (`UpdateMailboxRequest`): `mailbox` (MailboxUpdate, required), `expected_metadata_version` (string), `account_id` (string), `reason` (string or null).

### Permanently delete an archived mailbox

`DELETE /v1/mailboxes/{mailbox_id}` · [web reference](https://revdoku.com/api/reference/mailboxes.md#permanently-delete-an-archived-mailbox)

`client.api.delete_mailbox(mailbox_id, delete_mailbox_request)`

Archive the mailbox first. Send delete.confirmation from the mailbox read after the user confirms. Large mailboxes finish deleting in the background.

Parameters: `mailbox_id` (string, required).

Body `delete_mailbox_request` (`DeleteMailboxRequest`): `confirmation` (string, required), `account_id` (string), `reason` (string or null).

### Archive a mailbox

`POST /v1/mailboxes/{mailbox_id}/archive` · [web reference](https://revdoku.com/api/reference/mailboxes.md#archive-a-mailbox)

`client.api.archive_mailbox(mailbox_id, action_request)`

Archived mailboxes keep their files and emails and become read-only.

Parameters: `mailbox_id` (string, required).

Body `action_request` (`ActionRequest`): `account_id` (string), `reason` (string or null).

### Unarchive a mailbox

`POST /v1/mailboxes/{mailbox_id}/unarchive` · [web reference](https://revdoku.com/api/reference/mailboxes.md#unarchive-a-mailbox)

`client.api.unarchive_mailbox(mailbox_id, action_request)`

Requires mailbox-admin permission. The mailbox becomes writable again. If another active mailbox has the same title, the title gets a number suffix. A mailbox that is not archived returns MAILBOX_NOT_ARCHIVED.

Parameters: `mailbox_id` (string, required).

Body `action_request` (`ActionRequest`): `account_id` (string), `reason` (string or null).

## Email settings

### Read address settings

`GET /v1/mailboxes/{mailbox_id}/email` · [web reference](https://revdoku.com/api/reference/email-settings.md#read-address-settings)

`client.api.get_mailbox_email_settings(mailbox_id)`

Requires mailbox write permission.

Parameters: `mailbox_id` (string, required), `account_id` (string), `reason` (string or null).

### Change the primary address

`POST /v1/mailboxes/{mailbox_id}/email/rotate` · [web reference](https://revdoku.com/api/reference/email-settings.md#change-the-primary-address)

`client.api.change_mailbox_address(mailbox_id, change_mailbox_address_request)`

Requires mailbox admin permission and a paid plan, except for a change back to revdokumail. com. Send the current address as expected_address. Omit username for a generated name. A custom-domain change returns 202; read the settings until assignment.status is active or failed. For account owners and administrators the old address becomes an alias unless keep_old_as_alias is false. Without a free alias slot the request returns EMAIL_ALIAS_LIMIT; send false to retire the old address. A change from revdokumail.com to a customer domain always keeps the old address as the revdokumail.com base address, which uses no alias slot. A change from a customer domain back to revdokumail.com makes that base address the main address again at once (200, assignment.status active): username is ignored, no address change is counted and it works on every plan.

Parameters: `mailbox_id` (string, required).

Body `change_mailbox_address_request` (`ChangeMailboxAddressRequest`): `confirm` (boolean `true`, required), `expected_address` (string, required), `username` (string), `domain` (string), `keep_old_as_alias` (boolean), `account_id` (string), `reason` (string or null).

### Add an alias address

`POST /v1/mailboxes/{mailbox_id}/email/aliases` · [web reference](https://revdoku.com/api/reference/email-settings.md#add-an-alias-address)

`client.api.create_email_alias(mailbox_id, create_email_alias_request)`

Requires a paid plan and a full-account owner or administrator with mailbox-admin permission. The primary address stays unchanged. On a mailbox whose primary address is on your domain, the first revdokumail.com alias becomes its base address and uses no alias slot.

Parameters: `mailbox_id` (string, required).

Body `create_email_alias_request` (`CreateEmailAliasRequest`): `username` (string, required), `domain` (string), `account_id` (string), `reason` (string or null).

### Remove an alias address

`DELETE /v1/mailboxes/{mailbox_id}/email/aliases/{alias_id}` · [web reference](https://revdoku.com/api/reference/email-settings.md#remove-an-alias-address)

`client.api.delete_email_alias(mailbox_id, alias_id)`

Stops new and queued deliveries to the alias. Saved emails stay. The base address of a mailbox whose primary address is on your domain cannot be removed (`409 EMAIL_ALIAS_BASE`).

Parameters: `mailbox_id` (string, required), `alias_id` (string, required), `account_id` (string), `reason` (string or null).

### Replace the allowed senders

`PATCH /v1/mailboxes/{mailbox_id}/email/allowlist` · [web reference](https://revdoku.com/api/reference/email-settings.md#replace-the-allowed-senders)

`client.api.update_email_allowlist(mailbox_id, update_email_allowlist_request)`

Requires an account owner or administrator with mailbox-admin permission. Send sender_allowlist.version from the settings read as expected_version.

Parameters: `mailbox_id` (string, required).

Body `update_email_allowlist_request` (`UpdateEmailAllowlistRequest`): `sender_allowlist` (object, required), `expected_version` (string, required), `account_id` (string), `reason` (string or null).

### Read the email webhook

`GET /v1/mailboxes/{mailbox_id}/email/webhook` · [web reference](https://revdoku.com/api/reference/email-settings.md#read-the-email-webhook)

`client.api.get_email_webhook(mailbox_id)`

Requires mailbox-admin permission. webhook is null when no webhook is set. The signing secret is never returned here.

Parameters: `mailbox_id` (string, required), `account_id` (string).

### Set the email webhook

`PUT /v1/mailboxes/{mailbox_id}/email/webhook` · [web reference](https://revdoku.com/api/reference/email-settings.md#set-the-email-webhook)

`client.api.set_email_webhook(mailbox_id, set_email_webhook_request)`

Requires mailbox-admin permission and a public HTTPS URL. A new URL or rotate_secret=true creates a new signing secret, returns it once and cancels pending deliveries. The same URL without rotate_secret returns the webhook without a secret.

Parameters: `mailbox_id` (string, required).

Body `set_email_webhook_request` (`SetEmailWebhookRequest`): `webhook_url` (string (uri), required), `rotate_secret` (boolean), `account_id` (string), `reason` (string or null).

### Remove the email webhook

`DELETE /v1/mailboxes/{mailbox_id}/email/webhook` · [web reference](https://revdoku.com/api/reference/email-settings.md#remove-the-email-webhook)

`client.api.delete_email_webhook(mailbox_id)`

Cancels queued deliveries. A delivery already in progress can finish. Returns the mailbox ID, also when no webhook is set.

Parameters: `mailbox_id` (string, required), `account_id` (string).

### Get a live email subscription ticket

`GET /v1/mailboxes/{mailbox_id}/email/subscription` · [web reference](https://revdoku.com/api/reference/email-settings.md#get-a-live-email-subscription-ticket)

`client.api.get_email_subscription(mailbox_id)`

Requires mailbox read permission. Connect to websocket_url with email_subscription_token=TOKEN within 60 seconds, then subscribe to EmailReceivedChannel. Catch up with the email list cursor after every connect.

Parameters: `mailbox_id` (string, required), `account_id` (string).

## Emails

### List emails

`GET /v1/mailboxes/{mailbox_id}/emails` · [web reference](https://revdoku.com/api/reference/emails.md#list-emails)

`client.list_emails(mailbox_id)`. Full API: `client.api.list_emails(mailbox_id)`.

Requires mailbox read permission. Lists received email by default. To poll, list in ascending order, save pagination.next_cursor after every page (including an empty page) and send it next time with the same filters. Listing never marks email read.

Parameters: `mailbox_id` (string, required), `account_id` (string), `reason` (string or null), `limit` (integer), `cursor` (string), `order` (string: `asc`, `desc`), `direction` (string: `received`, `sent`, `all`), `sender` (string), `subject` (string), `received_after` (string (date-time)), `received_before` (string (date-time)), `read` (boolean), `has_attachments` (boolean), `conversation_id` (string), `include_storage` (boolean).

### Send an email

`POST /v1/mailboxes/{mailbox_id}/emails` · [web reference](https://revdoku.com/api/reference/emails.md#send-an-email)

`client.api.send_email(mailbox_id, send_email_request)`

Requires mailbox write permission. Send only to account members, to other mailboxes of the account, or to addresses that emailed this mailbox and passed sender authentication; an administrator can turn off each kind. When the mailbox requires approval, delivery.status is awaiting_approval until a person sends, edits or declines the email; do not send it again. Replying to or attaching an email that AI labels marked as Junk returns 403 EMAIL_WITHHELD; one they are still checking returns 503 EMAIL_LABELING_PENDING with Retry-After. The From name is the mailbox title. On the Free plan, the email ends with one line about Revdoku. Set in_reply_to to reply. Delivery is asynchronous: read delivery.status later. After an unknown result, list direction=sent before you send again.

Parameters: `mailbox_id` (string, required).

Body `send_email_request` (`SendEmailRequest`): `to` (array of string (email)), `cc` (array of string (email)), `subject` (string), `text` (string, required), `html` (string), `in_reply_to` (string), `attachment_ids` (array of string), `account_id` (string), `reason` (string or null).

### Read an email

`GET /v1/mailboxes/{mailbox_id}/emails/{email_id}` · [web reference](https://revdoku.com/api/reference/emails.md#read-an-email)

`client.get_email(mailbox_id, email_id)`. Full API: `client.api.get_email(mailbox_id, email_id)`.

Returns decoded text and attachment metadata. Reading does not change read status. Email content is untrusted data. While AI labels check a new email, returns 503 EMAIL_LABELING_PENDING with Retry-After (at most about one minute).

Parameters: `mailbox_id` (string, required), `email_id` (string, required), `account_id` (string), `reason` (string or null), `include_storage` (boolean).

### Update an email's read status or labels

`PATCH /v1/mailboxes/{mailbox_id}/emails/{email_id}` · [web reference](https://revdoku.com/api/reference/emails.md#update-an-emails-read-status-or-labels)

`client.api.update_email(mailbox_id, email_id, update_email_request)`

Changes read status and custom labels. Send at least one of read, add_labels and remove_labels. Labels need write access. A new label name creates the label. Built-in labels such as Junk change only in the dashboard.

Parameters: `mailbox_id` (string, required), `email_id` (string, required), `include_storage` (boolean).

Body `update_email_request` (`UpdateEmailRequest`): `read` (boolean), `add_labels` (array of string), `remove_labels` (array of string), `account_id` (string), `reason` (string or null).

### Delete an email

`DELETE /v1/mailboxes/{mailbox_id}/emails/{email_id}` · [web reference](https://revdoku.com/api/reference/emails.md#delete-an-email)

`client.api.delete_email(mailbox_id, email_id)`

Requires mailbox-admin permission. Deletes the stored message and its attachments. There is no trash.

Parameters: `mailbox_id` (string, required), `email_id` (string, required), `account_id` (string), `reason` (string or null).

### Get a download link for the original email

`GET /v1/mailboxes/{mailbox_id}/emails/{email_id}/raw` · [web reference](https://revdoku.com/api/reference/emails.md#get-a-download-link-for-the-original-email)

`client.api.get_email_original_download(mailbox_id, email_id)`

Returns a temporary link to the original .eml file. Downloads do not change read status. Junk email returns 403 EMAIL_WITHHELD. A new email that AI labels are still checking returns 503 EMAIL_LABELING_PENDING with Retry-After.

Parameters: `mailbox_id` (string, required), `email_id` (string, required), `account_id` (string), `reason` (string or null).

### Get a download link for an attachment

`GET /v1/mailboxes/{mailbox_id}/emails/{email_id}/attachments/{attachment_id}` · [web reference](https://revdoku.com/api/reference/emails.md#get-a-download-link-for-an-attachment)

`client.get_attachment_download(mailbox_id, email_id, attachment_id)`. Full API: `client.api.get_email_attachment_download(mailbox_id, email_id, attachment_id)`.

Returns a temporary link. No extraction or analysis is done. Junk email returns 403 EMAIL_WITHHELD. A new email that AI labels are still checking returns 503 EMAIL_LABELING_PENDING with Retry-After.

Parameters: `mailbox_id` (string, required), `email_id` (string, required), `attachment_id` (string, required), `account_id` (string), `reason` (string or null).

## Files

### Prepare a file upload (step 1 of 3)

`POST /v1/direct_uploads` · [web reference](https://revdoku.com/api/reference/files.md#prepare-a-file-upload-step-1-of-3)

`client.upload_file(mailbox_id, path, content)` (runs all three upload steps). Full API: `client.api.prepare_file_upload(prepare_file_upload_request)`.

Returns a storage URL. Then PUT the bytes to direct_upload.url with exactly direct_upload.headers and no API key (step 2), and save the file with POST /v1/mailboxes/{mailbox_id}/files (step 3). Identical content at the same path returns skipped=true and duplicate=true without an upload.

Body `prepare_file_upload_request` (`PrepareFileUploadRequest`): `mailbox_id` (string, required), `path` (string, required), `existing_file_policy` (string: `replace`, `skip`), `blob` (UploadBlob, required), `account_id` (string), `reason` (string or null).

### List files

`GET /v1/mailboxes/{mailbox_id}/files` · [web reference](https://revdoku.com/api/reference/files.md#list-files)

`client.list_files(mailbox_id)`. Full API: `client.api.list_files(mailbox_id)`.

Lists current files, including stored emails under _email/. Listing never marks files read.

Parameters: `mailbox_id` (string, required), `account_id` (string), `reason` (string or null), `q` (string), `folder` (string), `limit` (integer), `cursor` (string).

### Save an uploaded file (step 3 of 3)

`POST /v1/mailboxes/{mailbox_id}/files` · [web reference](https://revdoku.com/api/reference/files.md#save-an-uploaded-file-step-3-of-3)

`client.upload_file(mailbox_id, path, content)` (runs all three upload steps). Full API: `client.api.save_uploaded_file(mailbox_id, save_uploaded_file_request)`.

Saves the uploaded blob at path. An existing path gets a new version.

Parameters: `mailbox_id` (string, required).

Body `save_uploaded_file_request` (`SaveUploadedFileRequest`): `path` (string, required), `signed_blob_id` (string, required), `name` (string), `role` (string: `source`, `reference`, `generated`, `agent_output`, `export`, `artifact`), `existing_file_policy` (string: `replace`, `skip`), `expected_mailbox_version` (string), `account_id` (string), `reason` (string or null).

### Find a file by path

`GET /v1/mailboxes/{mailbox_id}/files/by_path` · [web reference](https://revdoku.com/api/reference/files.md#find-a-file-by-path)

`client.api.get_file_by_path(mailbox_id, path)`

Returns file metadata only. Read content with the download endpoint. The disposition and content_url parameters return INVALID_ARGUMENT.

Parameters: `mailbox_id` (string, required), `path` (string, required), `account_id` (string), `reason` (string or null).

### Append text to a file

`POST /v1/mailboxes/{mailbox_id}/files/append_text` · [web reference](https://revdoku.com/api/reference/files.md#append-text-to-a-file)

`client.api.append_text(mailbox_id, append_text_request)`

Appends UTF-8 text to an existing text file and creates a new version. A missing file returns MAILBOX_FILE_NOT_FOUND.

Parameters: `mailbox_id` (string, required).

Body `append_text_request` (`AppendTextRequest`): `path` (string, required), `content` (string, required), `newline_before` (boolean), `expected_mailbox_version` (string), `account_id` (string), `reason` (string or null).

### Read file metadata

`GET /v1/mailboxes/{mailbox_id}/files/{file_id}` · [web reference](https://revdoku.com/api/reference/files.md#read-file-metadata)

`client.api.get_file(mailbox_id, file_id)`

Reading metadata never marks the file read.

Parameters: `mailbox_id` (string, required), `file_id` (string, required), `account_id` (string), `reason` (string or null).

### Delete a file

`DELETE /v1/mailboxes/{mailbox_id}/files/{file_id}` · [web reference](https://revdoku.com/api/reference/files.md#delete-a-file)

`client.api.delete_file(mailbox_id, file_id)`

Requires mailbox-admin permission. Files under _email/ return EMAIL_PATH_READ_ONLY; delete the email instead. Other top-level folders that start with _ return RESERVED_PATH.

Parameters: `mailbox_id` (string, required), `file_id` (string, required), `account_id` (string), `reason` (string or null).

### Get a download link for a file

`GET /v1/mailboxes/{mailbox_id}/files/{file_id}/download` · [web reference](https://revdoku.com/api/reference/files.md#get-a-download-link-for-a-file)

`client.api.get_file_download(mailbox_id, file_id)`

Returns a temporary link and marks this version read. Send version_id for an older version.

Parameters: `mailbox_id` (string, required), `file_id` (string, required), `version_id` (string), `account_id` (string), `reason` (string or null).

### Rename or move a file in the same mailbox

`POST /v1/mailboxes/{mailbox_id}/files/{file_id}/rename` · [web reference](https://revdoku.com/api/reference/files.md#rename-or-move-a-file-in-the-same-mailbox)

`client.api.rename_file(mailbox_id, file_id, rename_file_request)`

Changes the path without uploading the content again.

Parameters: `mailbox_id` (string, required), `file_id` (string, required).

Body `rename_file_request` (`RenameFileRequest`): `new_path` (string, required), `account_id` (string), `reason` (string or null).

### Move a file

`POST /v1/mailboxes/{mailbox_id}/files/{file_id}/move` · [web reference](https://revdoku.com/api/reference/files.md#move-a-file)

`client.api.move_file(mailbox_id, file_id, move_file_request)`

Works in the same mailbox or into target_mailbox_id. Content is not uploaded again. Send target_path for an exact path or target_folder to keep the name.

Parameters: `mailbox_id` (string, required), `file_id` (string, required).

Body `move_file_request` (`MoveFileRequest`): `target_mailbox_id` (string), `target_path` (string), `target_folder` (string), `account_id` (string), `reason` (string or null).

### Copy a file

`POST /v1/mailboxes/{mailbox_id}/files/{file_id}/copy` · [web reference](https://revdoku.com/api/reference/files.md#copy-a-file)

`client.api.copy_file(mailbox_id, file_id, move_file_request)`

Works in the same mailbox or into target_mailbox_id. Content is not uploaded again. Send target_path for an exact path or target_folder to keep the name.

Parameters: `mailbox_id` (string, required), `file_id` (string, required).

Body `move_file_request` (`MoveFileRequest`): `target_mailbox_id` (string), `target_path` (string), `target_folder` (string), `account_id` (string), `reason` (string or null).

### List file versions

`GET /v1/mailboxes/{mailbox_id}/files/{file_id}/versions` · [web reference](https://revdoku.com/api/reference/files.md#list-file-versions)

`client.api.list_file_versions(mailbox_id, file_id)`

Newest first.

Parameters: `mailbox_id` (string, required), `file_id` (string, required), `account_id` (string), `reason` (string or null), `limit` (integer), `cursor` (string).

### Restore a file version

`POST /v1/mailboxes/{mailbox_id}/files/{file_id}/versions/{version_id}/restore` · [web reference](https://revdoku.com/api/reference/files.md#restore-a-file-version)

`client.api.restore_file_version(mailbox_id, file_id, version_id, action_request)`

Creates a new current version with the content of the selected version. History is kept. Requires a plan with version restore.

Parameters: `mailbox_id` (string, required), `file_id` (string, required), `version_id` (string, required).

Body `action_request` (`ActionRequest`): `account_id` (string), `reason` (string or null).

### Start a batch upload

`POST /v1/mailboxes/{mailbox_id}/upload_sessions` · [web reference](https://revdoku.com/api/reference/files.md#start-a-batch-upload)

`client.api.create_upload_session(mailbox_id, create_upload_session_request)`

Starts an upload session for many files and returns storage targets for the first files. The session locks the mailbox for other writers; incoming email still arrives. Send files in batches with POST .../uploads, PUT the bytes to each upload.url, save each batch with POST .../finalize_batch, then call POST .../finalize. Unsaved uploads are discarded when the session expires.

Parameters: `mailbox_id` (string, required).

Body `create_upload_session_request` (`CreateUploadSessionRequest`): `files` (array of UploadSessionFile), `expected_file_count` (integer), `client_session_key` (string), `existing_file_policy` (string: `replace`, `skip`), `expected_mailbox_version` (string), `account_id` (string), `reason` (string or null).

### Get storage targets for a batch

`POST /v1/mailboxes/{mailbox_id}/upload_sessions/{session_id}/uploads` · [web reference](https://revdoku.com/api/reference/files.md#get-storage-targets-for-a-batch)

`client.api.add_upload_session_files(mailbox_id, session_id, add_upload_session_files_request)`

Returns upload.url and upload.headers for each file that needs bytes. Repeating a path returns a fresh target, for example after a failed PUT. Files with identical content are skipped.

Parameters: `mailbox_id` (string, required), `session_id` (string, required).

Body `add_upload_session_files_request` (`AddUploadSessionFilesRequest`): `files` (array of UploadSessionFile, required), `account_id` (string), `reason` (string or null).

### Save uploaded files

`POST /v1/mailboxes/{mailbox_id}/upload_sessions/{session_id}/finalize_batch` · [web reference](https://revdoku.com/api/reference/files.md#save-uploaded-files)

`client.api.save_upload_session_batch(mailbox_id, session_id)`

Saves up to limit files whose bytes were uploaded. Call it after each batch to keep each request short. DIRECT_UPLOAD_NOT_FOUND names a file whose bytes are missing in error.details.path; upload it again and retry.

Parameters: `mailbox_id` (string, required), `session_id` (string, required).

Body `save_upload_session_batch_request` (`SaveUploadSessionBatchRequest`, optional): `limit` (integer), `account_id` (string), `reason` (string or null).

### Finish or cancel a batch upload

`POST /v1/mailboxes/{mailbox_id}/upload_sessions/{session_id}/finalize` · [web reference](https://revdoku.com/api/reference/files.md#finish-or-cancel-a-batch-upload)

`client.api.finalize_upload_session(mailbox_id, session_id)`

complete=true saves the remaining uploaded files, creates one mailbox version and releases the lock. A 202 response with finalize_pending=true means more files remain: call finalize again after Retry-After. complete=false cancels the session and discards its unsaved files. Finalizing a finished session returns it unchanged.

Parameters: `mailbox_id` (string, required), `session_id` (string, required).

Body `finalize_upload_session_request` (`FinalizeUploadSessionRequest`, optional): `complete` (boolean), `account_id` (string), `reason` (string or null).

## Email domains

### List custom email domains

`GET /v1/account/email_domains` · [web reference](https://revdoku.com/api/reference/email-domains.md#list-custom-email-domains)

`client.api.list_email_domains()`

Requires a full-account owner or administrator credential.

Parameters: `account_id` (string), `limit` (integer), `cursor` (string).

### Connect a custom email domain

`POST /v1/account/email_domains` · [web reference](https://revdoku.com/api/reference/email-domains.md#connect-a-custom-email-domain)

`client.api.create_email_domain(create_email_domain_request)`

Claims an exact hostname and returns the ownership record. Read the domain again shortly after for all `required_dns_records`. Never change DNS without the domain owner's authorization.

Body `create_email_domain_request` (`CreateEmailDomainRequest`): `hostname` (string, required), `account_id` (string), `reason` (string or null).

### Check a hostname for conflicting DNS

`POST /v1/account/email_domains/check` · [web reference](https://revdoku.com/api/reference/email-domains.md#check-a-hostname-for-conflicting-dns)

`client.api.check_email_domain(create_email_domain_request)`

Makes no claim and changes no DNS. If the root domain already receives email, use an unused subdomain such as inbox.example.com.

Body `create_email_domain_request` (`CreateEmailDomainRequest`): `hostname` (string, required), `account_id` (string), `reason` (string or null).

### Read a custom email domain

`GET /v1/account/email_domains/{domain_id}` · [web reference](https://revdoku.com/api/reference/email-domains.md#read-a-custom-email-domain)

`client.api.get_email_domain(domain_id)`

Requires a full-account owner or administrator credential. Returns the domain status and the DNS records to publish.

Parameters: `domain_id` (string, required), `account_id` (string).

### Remove an unused custom email domain

`DELETE /v1/account/email_domains/{domain_id}` · [web reference](https://revdoku.com/api/reference/email-domains.md#remove-an-unused-custom-email-domain)

`client.api.delete_email_domain(domain_id, delete_email_domain_request)`

Send the domain hostname and confirm=true. A domain that mailbox addresses still use returns EMAIL_DOMAIN_IN_USE.

Parameters: `domain_id` (string, required).

Body `delete_email_domain_request` (`DeleteEmailDomainRequest`): `hostname` (string, required), `confirm` (boolean `true`, required), `account_id` (string), `reason` (string or null).

### Check DNS and provider setup again

`POST /v1/account/email_domains/{domain_id}/verify` · [web reference](https://revdoku.com/api/reference/email-domains.md#check-dns-and-provider-setup-again)

`client.api.verify_email_domain(domain_id, verify_email_domain_request)`

Queues the check and returns the current state. Read the domain again to see the result.

Parameters: `domain_id` (string, required).

Body `verify_email_domain_request` (`VerifyEmailDomainRequest`): `account_id` (string), `reason` (string or null).

### Get a one-click DNS setup link

`GET /v1/account/email_domains/{domain_id}/setup_link` · [web reference](https://revdoku.com/api/reference/email-domains.md#get-a-one-click-dns-setup-link)

`client.api.get_email_domain_setup_link(domain_id)`

Signs a Domain Connect link for a domain whose `setup_provider` is set. Give the URL to the domain owner to open in a browser. The DNS provider adds `required_dns_records` after the owner approves them, then returns to Account Settings → Domains. Errors: 422 `EMAIL_DOMAIN_SETUP_UNSUPPORTED` when the provider or the domain state does not allow one-click setup, 422 `EMAIL_DOMAIN_SETUP_UNAVAILABLE` while the deployment cannot sign links, 422 `EMAIL_DNS_CONFLICT` when the hostname has records of another mail provider, 403 `EMAIL_DOMAINS_UPGRADE_REQUIRED` when the plan no longer includes custom email domains, and 503 `EMAIL_DNS_TEMPORARY` when DNS cannot be checked. Add the records manually, or try again later after a 503.

Parameters: `domain_id` (string, required), `account_id` (string).
