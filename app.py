import os
import json
import string
import random
import datetime

# these 3 imports are related to auto deployment. for more
# details, check the comments near the verify_signature funcion
import hmac
import hashlib
import subprocess

import pytz

from flask import Flask, render_template, request, redirect, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

load_dotenv()

app = Flask("-- shl --")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
# the above line was added because i plan to use this app behind a proxy
# you can remove it if you are not behind a proxy

# this variable is related to auto deploymet. remove if not needed
APP_SECRET_TOKEN = os.environ.get("APP_SECRET_TOKEN")

CHARACTERS = string.ascii_letters + string.digits
JSON_FILES_PATH = os.environ.get("JSON_FILES_PATH", "links/")
# the details for a sh link are and will be stored in this path
BASE_URL = os.environ.get("BASE_URL")
# this is the base url of the app. if running locally, set it to
# your local ip and port
MIN_LENGTH_ID = os.environ.get("MIN_LENGTH_ID", 2)
MAX_LENGTH_ID = os.environ.get("MAX_LENGTH_ID", 8)

if not os.path.exists(JSON_FILES_PATH):
    os.makedirs(os.path.abspath(JSON_FILES_PATH), exist_ok=True)

# the thing below is nice if you re going to mess with the html/python
# code for a while. with this, you dont have to restart gunicorn every
# time a change has been made
if os.environ.get("DEBUG_MODE") == "debug_reload":
    print("[SHL] Running in debug mode")

    app.config["DEBUG"] = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True


def generate_id():
    length = random.randint(MIN_LENGTH_ID, MAX_LENGTH_ID)

    return "".join(random.choice(CHARACTERS) for _ in range(length))


def is_valid_id(link_id):
    valid_chars = 0
    link_id_len = len(link_id)

    if link_id_len > MAX_LENGTH_ID or link_id_len < MIN_LENGTH_ID:
        return False

    for letter in link_id:
        if letter in CHARACTERS:
            valid_chars += 1

    return True if valid_chars == link_id_len else False


def get_link(link_id):
    try:
        with open(
            f"{JSON_FILES_PATH}/{link_id}.json", "r", encoding="utf-8"
        ) as shl_link:
            return {"status": "good", "data": json.load(shl_link)}

    except FileNotFoundError:
        return {
            "status": "bad",
            "data": {"error": f"shl link with ID '{link_id}' was not found"},
        }


def create_link(link_redirect, link_id=None):
    shl_id = link_id or generate_id()

    if link_id:
        if not is_valid_id(link_id):
            return {
                "status": "bad",
                "data": {
                    "error": f"id given '{link_id}' is not valid. id must contain only letters and numbers, and must not exceed the limit of {MAX_LENGTH_ID} characters, or be less than {MIN_LENGTH_ID} characters in total"
                },
            }

    while get_link(shl_id)["status"] == "good":
        shl_id = generate_id()

    data = {
        "link_created_timestamp": datetime.datetime.now(pytz.UTC).timestamp(),
        "link_id": shl_id,
        "link_redirects_to": link_redirect,
        "link_shlink": f"{BASE_URL}/r/{shl_id}",
    }

    with open(f"{JSON_FILES_PATH}/{shl_id}.json", "w+", encoding="utf-8") as shl_link:
        json.dump(data, shl_link, indent=4)

    return get_link(shl_id)


# you will probably not need this function and the /autod route,
# unless you set up auto deployment manually by yourself, like im doing
# if you are not, remove this function and the /autod route
def verify_signature(secret_token, signature_header, payload_body):
    if not signature_header:
        return False

    expected = (
        "sha256="
        + hmac.new(secret_token.encode(), payload_body, hashlib.sha256).hexdigest()
    )

    return hmac.compare_digest(expected, signature_header)


@app.route("/autod", methods=["POST"])
def autod():
    signature = request.headers.get("X-Hub-Signature-256")
    payload = request.get_data()

    if verify_signature(APP_SECRET_TOKEN, signature, payload):
        subprocess.Popen([os.path.abspath("re-deploy.sh")])

        return "", 200

    else:
        return "", 403


@app.route("/")
def main_route():
    total_shlinks = len(os.listdir(JSON_FILES_PATH))

    return render_template("index.html", total_shlinks=total_shlinks)


@app.route("/get")
def get_route():
    link_id = request.args.get("link_id")

    shl_data = get_link(link_id)

    if shl_data["status"] == "good":
        return render_template("get.html", shl_data=shl_data, datetime=datetime)

    else:
        return render_template("notfound.html", link_id=link_id)


@app.route("/create")
def create_route():
    link_id = request.args.get("link_id")
    link_redirect = request.args.get("link_redirect")

    shl_data = create_link(link_redirect, link_id)

    return render_template("create.html", shl_data=shl_data, datetime=datetime)


@app.route("/r/<link_id>")
def redirect_route(link_id):
    shl_data = get_link(link_id)

    if shl_data["status"] == "good":
        return redirect(shl_data["data"]["link_redirects_to"])

    else:
        return render_template("notfound.html", link_id=link_id)


@app.route("/api")
def api_route():
    return render_template("api.html")


@app.route("/api/get")
def api_get_route():
    link_id = request.args.get("link_id")

    if not link_id:
        return jsonify({"status": "bad", "error": "missing link_id parameter"})

    return jsonify(get_link(link_id))


@app.route("/api/create")
def api_create_route():
    link_id = request.args.get("link_id")
    link_redirect = request.args.get("link_redirect")

    if not link_redirect:
        return jsonify({"status": "bad", "error": "missing link_redirect parameter"})

    if link_id:
        return jsonify(create_link(link_redirect, link_id))

    else:
        return jsonify(create_link(link_redirect))
