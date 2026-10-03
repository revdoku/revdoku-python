# revdoku-api

Generated Revdoku API client, version 1.0.525. Email inboxes and private file storage.
Covers the endpoints in [OpenAPI](https://revdoku.com/openapi.json); the complete API reference is [api.md](https://revdoku.com/api.md).
Base URL: `https://api.revdoku.com` (generated paths include `/v1`). Configure a bearer API key privately; never embed it in source.

## First request

```python
import os
from revdoku_api import ApiClient, Configuration, DefaultApi

with ApiClient(Configuration(access_token=os.environ['REVDOKU_API_KEY'])) as client:
    result = DefaultApi(client).get_account_limits(account_id=os.getenv('REVDOKU_ACCOUNT_ID'))
    print(result.data)
```

`REVDOKU_ACCOUNT_ID` is optional. Set it to select an account explicitly granted to the credential; otherwise the credential's default account applies.
Success responses retain the API's `data` envelope. Read `data.email`, `data.bucket`, or `data.limits` for the corresponding resource.

## Runnable examples

[Four examples with setup and run commands](examples/README.md): create an inbox, read unread emails, download an attachment, and list stored files.

## Source and contributions

[Source, issues and pull requests](https://github.com/revdoku/revdoku-python). Contributions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md) for setup and the regeneration process.

Licensed under [MIT](LICENSE), including permission to use, modify and distribute the source. Support: support@revdoku.com.
