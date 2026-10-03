## First request

```python
import os
from revdoku_api import ApiClient, Configuration, DefaultApi

with ApiClient(Configuration(access_token=os.environ['REVDOKU_API_KEY'])) as client:
    result = DefaultApi(client).get_account_limits(account_id=os.getenv('REVDOKU_ACCOUNT_ID'))
    print(result.data)
```

Base URL: `https://api.revdoku.com`; generated paths include `/v1`. Keep your bearer API key in private configuration.
`REVDOKU_ACCOUNT_ID` is optional and selects an account granted to the key; otherwise its default account applies.
Read resource results from the API's `data` envelope, such as `data.email`, `data.bucket` or `data.limits`.

[Four runnable examples and source setup](examples/README.md) · [API reference](https://revdoku.com/api.md)
