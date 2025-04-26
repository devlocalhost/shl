# shl
shl - an easy to use, minimal, and fast url shortener. no bullshitting, no trackers, no ads, no javascript.

# running
1. install dependecies
```sh
pip install -r requirements.txt
```

2. setup your .env file
```
BASE_URL="https://example.com"
JSON_FILES_PATH="/home/me/shl/links"
```

3. run using gunicorn
```sh
gunicorn -b 0.0.0.0:5000 app:app
```

# usage
visit the index page for details. or, you can use the "api" endpoints, which are `/api/create` to create and `/api/get` to get results.

the get endpoint requires `link_id`, while the create endpoint requires `link_redirect`. you can pass `link_id` too, if youd like

example responses of `/api/get`:
```json
{
  "data": {
    "error": "shl link with ID 'lu' was not found"
  },
  "status": "bad"
}
```

```json
{
  "data": {
    "link_created_timestamp": 1745669087.938688,
    "link_id": "HPGc",
    "link_redirects_to": "https://dev64.xyz",
    "link_shlink": "http://192.168.1.77:5000/r/HPGc"
  },
  "status": "good"
}
```

example responses of `/api/create`:
```json
{
  "data": {
    "link_created_timestamp": 1745669162.01382,
    "link_id": "WhzGCD",
    "link_redirects_to": "https://google.com",
    "link_shlink": "http://192.168.1.77:5000/r/WhzGCD"
  },
  "status": "good"
}
```
