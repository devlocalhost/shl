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
