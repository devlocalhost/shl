import os
import json
import string
import random
import datetime

from flask import Flask, render_template, request, redirect, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

import pytz

app = Flask("-- shl --")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

JSON_FILES_PATH = os.environ.get("JSON_FILES_PATH", "links/")
BASE_URL = os.environ.get("BASE_URL")

if not os.path.exists(JSON_FILES_PATH):
    os.makedirs(os.path.abspath(JSON_FILES_PATH), exist_ok=True)

if os.environ.get("DEBUG_MODE") == "debug_reload":
    print("[SHL] Running in debug mode")

    app.config["DEBUG"] = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True


def generate_id():
    length = random.randint(2, 6)
    characters = string.ascii_letters + string.digits

    return "".join(random.choice(characters) for _ in range(length))


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

    while get_link(shl_id)["status"] == "good":
        shl_id = generate_id()

    data = {
        "link_created_timestamp": datetime.datetime.now(pytz.UTC).timestamp(),
        "link_id": shl_id,
        "link_redirects_to": link_redirect,
        "link_shlink": f"{BASE_URL}/r/{shl_id}"
    }

    with open(f"{JSON_FILES_PATH}/{shl_id}.json", "w+", encoding="utf-8") as shl_link:
        json.dump(data, shl_link, indent=4)

    return get_link(shl_id)


@app.route("/")
def main_route():
    return render_template("index.html")


@app.route("/get")
def get_route():
    link_id = request.args.get("link_id")

    shl_data = get_link(link_id)
    
    if shl_data['status'] == "good":
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

    if shl_data['status'] == "good":
        return redirect(shl_data['data']['link_redirect'])

    else:
        return render_template("notfound.html", link_id=link_id)
    

@app.route("/api")
def api_route():
    return "main api route. docs? no html. json"


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
