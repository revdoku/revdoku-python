"""Revdoku client for Python. Mutations are never retried automatically."""

from __future__ import annotations

import json
import math
import os
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Union
from urllib.parse import urlsplit

import urllib3

from .api.default_api import DefaultApi
from .api_client import ApiClient
from .api_response import ApiResponse
from .configuration import Configuration
from .exceptions import ApiException
from .models.create_project_request import CreateProjectRequest
from .models.project_create import ProjectCreate
from .models.project_email_options import ProjectEmailOptions
from .models.ticket_reply_request import TicketReplyRequest

if TYPE_CHECKING:
    from .models.create_project201_response import CreateProject201Response
    from .models.get_ticket200_response import GetTicket200Response
    from .models.get_ticket_message_original_download200_response import GetTicketMessageOriginalDownload200Response
    from .models.list_ticket_messages200_response import ListTicketMessages200Response
    from .models.list_tickets200_response import ListTickets200Response
    from .models.reply_to_ticket202_response import ReplyToTicket202Response
    from .models.get_ticket_message200_response import GetTicketMessage200Response
    from .models.list_files200_response import ListFiles200Response
    from .models.list_projects200_response import ListProjects200Response

DEFAULT_BASE_URL = "https://api.revdoku.com"
LOCAL_HOSTS = ("localhost", "127.0.0.1", "::1")


def _retry_after(value: Optional[str]) -> Optional[int]:
    """The Retry-After header in whole seconds: a number of seconds or an HTTP date. None when absent or invalid."""
    text = (value or "").strip()
    if re.fullmatch(r"[0-9]+", text):
        return int(text)
    try:
        date = parsedate_to_datetime(text)
    except (TypeError, ValueError, IndexError, OverflowError):
        return None
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)
    return max(0, math.ceil((date - datetime.now(timezone.utc)).total_seconds()))


def _check_timeout(value: Any) -> Any:
    """A positive number of seconds, or a (connect, read) pair of them. The generated
    REST client would treat 0 and any other value as no timeout."""
    def positive(number: Any) -> bool:
        return (not isinstance(number, bool) and isinstance(number, (int, float))
                and math.isfinite(number) and number > 0)
    if positive(value) or (isinstance(value, tuple) and len(value) == 2 and all(positive(item) for item in value)):
        return value
    raise ValueError("_request_timeout must be a positive number of seconds or a (connect, read) pair")


class RevdokuError(ApiException):
    """An error response from the Revdoku API. Branch on ``code``.
    ``retry_after`` is the Retry-After header in seconds, or None."""

    def __init__(self, message: str, status: int, code: str, details: Any = None,
                 request_id: Optional[str] = None, retry_after: Optional[int] = None) -> None:
        super().__init__(status=status)
        self.message = message
        self.code = code
        self.details = details
        self.request_id = request_id
        self.retry_after = retry_after

    def __str__(self) -> str:
        return f"{self.message} (HTTP {self.status} {self.code})"

    @classmethod
    def from_exception(cls, error: ApiException) -> "RevdokuError":
        try:
            body = json.loads(error.body or "")
        except (TypeError, ValueError):
            body = None
        payload = body.get("error") if isinstance(body, dict) else None
        payload = payload if isinstance(payload, dict) else {}
        status = error.status or 0
        message, code = payload.get("message"), payload.get("code")
        result = cls(message if isinstance(message, str) and message else f"HTTP {status}", status,
                     code if isinstance(code, str) and code else "HTTP_ERROR", payload.get("details"),
                     payload.get("request_id"), _retry_after((error.headers or {}).get("Retry-After")))
        result.reason, result.body, result.data, result.headers = error.reason, error.body, error.data, error.headers
        return result


class _Pool(urllib3.PoolManager):
    """Never retries a request or follows a redirect, so credentials stay on one origin."""

    def urlopen(self, method: str, url: str, redirect: bool = True, **kw: Any) -> Any:  # type: ignore[override]
        kw["retries"] = False
        return super().urlopen(method, url, redirect=False, **kw)


class _ApiClient(ApiClient):
    """Generated client with a default timeout and RevdokuError for every API error response.
    Network, timeout and TLS failures stay urllib3 exceptions."""

    def __init__(self, configuration: Configuration, timeout: float) -> None:
        super().__init__(configuration)
        self._timeout = timeout
        self.rest_client.pool_manager = _Pool(**self.rest_client.pool_manager.connection_pool_kw)

    def call_api(self, method: str, url: str, header_params: Any = None, body: Any = None,
                 post_params: Any = None, _request_timeout: Any = None) -> Any:
        timeout = self._timeout if _request_timeout is None else _check_timeout(_request_timeout)
        try:
            return super().call_api(method, url, header_params, body, post_params, timeout)
        except ApiException as error:
            # The generated REST client turns a urllib3 SSLError into ApiException(status=0).
            # Raise the original, like every other network failure.
            if isinstance(error.__context__, urllib3.exceptions.SSLError):
                raise error.__context__ from None
            raise

    def response_deserialize(self, response_data: Any, response_types_map: Any = None) -> ApiResponse[Any]:
        try:
            return super().response_deserialize(response_data, response_types_map)
        except RevdokuError:
            raise
        except ApiException as error:
            raise RevdokuError.from_exception(error) from None


def _valid_origin(value: str) -> bool:
    try:
        url = urlsplit(value)
        url.port  # Raises ValueError for an invalid port.
    except ValueError:
        return False
    return (url.username is None and url.password is None and not url.query and not url.fragment
            and url.path in ("", "/") and bool(url.hostname)
            and (url.scheme == "https" or (url.scheme == "http" and url.hostname in LOCAL_HOSTS)))


class Revdoku:
    """Revdoku API client. ``api`` is the full generated API for less common operations."""

    api: DefaultApi

    def __init__(self, api_key: Optional[str] = None, account_id: Optional[str] = None,
                 base_url: Optional[str] = None, timeout: float = 30.0) -> None:
        """``api_key`` defaults to REVDOKU_API_KEY. ``base_url`` is an origin without /v1.
        ``timeout`` is in seconds: the total time of each API request, and the time to
        connect and to wait for each read of a storage transfer."""
        origin = base_url or DEFAULT_BASE_URL
        if not _valid_origin(origin):
            raise ValueError("base_url must be an HTTPS origin without /v1; HTTP is allowed for localhost")
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("timeout must be a positive number of seconds")
        key = api_key if api_key is not None else os.environ.get("REVDOKU_API_KEY")
        if not key:
            raise ValueError("Set api_key or REVDOKU_API_KEY")
        url = urlsplit(origin)
        self._account_id = account_id
        self._timeout = timeout
        # Local development storage can use HTTP only when the API itself does.
        self._local_http = url.scheme == "http"
        self._client = _ApiClient(Configuration(host=f"{url.scheme}://{url.netloc}", access_token=key, retries=False), timeout)
        self._storage = _Pool()
        self.api = DefaultApi(self._client)

    def __enter__(self) -> "Revdoku":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def close(self) -> None:
        """Closes pooled connections."""
        self._client.rest_client.pool_manager.clear()
        self._storage.clear()

    def _account(self, options: Dict[str, Any]) -> Dict[str, Any]:
        if options.get("account_id") is None:
            options["account_id"] = self._account_id
        return options

    def _storage_url(self, value: str) -> str:
        url = urlsplit(value)
        local = self._local_http and url.scheme == "http" and url.hostname in LOCAL_HOSTS
        if (url.scheme != "https" and not local) or not url.hostname or url.username is not None or url.password is not None:
            raise ValueError("Expected an HTTPS storage URL without credentials")
        return value

    def _storage_timeout(self, value: Union[None, float, Tuple[float, float]]) -> Any:
        """``_request_timeout`` as the generated API reads it: a number is the total time, a pair is (connect, read)."""
        if value is None:
            return self._timeout
        if isinstance(_check_timeout(value), tuple):
            return urllib3.Timeout(connect=value[0], read=value[1])
        return urllib3.Timeout(total=value)

    def list_projects(self, **filters: Any) -> ListProjects200Response:
        return self.api.list_projects(**self._account(filters))

    def get_project(self, project_id: str, **options: Any) -> CreateProject201Response:
        return self.api.get_project(project_id, **self._account(options))

    def create_project(self, username: Optional[str] = None, domain: Optional[str] = None,
                       title: Optional[str] = None, account_id: Optional[str] = None, *,
                       description: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None,
                       **options: Any) -> CreateProject201Response:
        """Creates one project with its email address. After an uncertain result, list projects before you create another.
        ``options`` (for example ``_request_timeout``) go to the API call."""
        email = ProjectEmailOptions(username=username, domain=domain) if username is not None or domain is not None else None
        return self.api.create_project(CreateProjectRequest(
            account_id=self._account_id if account_id is None else account_id,
            project=ProjectCreate(title=title, description=description, metadata=metadata, email=email)), **options)

    def list_tickets(self, project_id: str, **filters: Any) -> ListTickets200Response:
        """Lists support tickets, newest activity first. Poll with ``updated_after``."""
        return self.api.list_tickets(project_id, **self._account(filters))

    def get_ticket(self, project_id: str, ticket_id: str, **options: Any) -> GetTicket200Response:
        return self.api.get_ticket(project_id, ticket_id, **self._account(options))

    def list_ticket_messages(self, project_id: str, ticket_id: str, **filters: Any) -> ListTicketMessages200Response:
        """Lists the messages of a ticket, oldest first."""
        return self.api.list_ticket_messages(project_id, ticket_id, **self._account(filters))

    def get_ticket_message(self, project_id: str, ticket_id: str, message_id: str, **options: Any) -> GetTicketMessage200Response:
        return self.api.get_ticket_message(project_id, ticket_id, message_id, **self._account(options))

    def reply_to_ticket(self, project_id: str, ticket_id: str, text: str, html: Optional[str] = None,
                        subject: Optional[str] = None, attachment_ids: Optional[list] = None,
                        account_id: Optional[str] = None, **options: Any) -> ReplyToTicket202Response:
        """Replies to the requester of a ticket. After an uncertain result, read the ticket before you reply again.
        ``options`` (for example ``_request_timeout``) go to the API call."""
        return self.api.reply_to_ticket(project_id, ticket_id, TicketReplyRequest(
            text=text, html=html, subject=subject, attachment_ids=attachment_ids,
            account_id=self._account_id if account_id is None else account_id), **options)

    def list_files(self, project_id: str, **filters: Any) -> ListFiles200Response:
        return self.api.list_files(project_id, **self._account(filters))

    def get_attachment_download(self, project_id: str, ticket_id: str, message_id: str, attachment_id: str,
                                **options: Any) -> GetTicketMessageOriginalDownload200Response:
        return self.api.get_ticket_message_attachment_download(project_id, ticket_id, message_id, attachment_id,
                                                               **self._account(options))

    def download_attachment(self, project_id: str, ticket_id: str, message_id: str, attachment_id: str,
                            max_bytes: int = 64 * 1024 * 1024, **options: Any) -> bytes:
        """Returns attachment bytes. Does not change shared read status or write local files.
        ``_request_timeout`` applies to the API call and to the storage download."""
        if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 0:
            raise ValueError("max_bytes must be a nonnegative integer")
        download = self.get_attachment_download(project_id, ticket_id, message_id, attachment_id, **options).data.download
        size = download.size_bytes
        if size is not None and size > max_bytes:
            raise ValueError("Attachment exceeds max_bytes")
        response = self._storage.request("GET", self._storage_url(download.url), preload_content=False,
                                         timeout=self._storage_timeout(options.get("_request_timeout")))
        try:
            if response.status != 200:
                raise RuntimeError(f"Attachment download failed: HTTP {response.status}")
            chunks, length = [], 0
            for chunk in response.stream(65536):
                length += len(chunk)
                if length > max_bytes:
                    raise ValueError("Attachment exceeds max_bytes")
                chunks.append(chunk)
        finally:
            response.close()
        if size is not None and length != size:
            raise ValueError("Attachment size does not match the download metadata")
        return b"".join(chunks)
