import os
import hashlib

import requests
import yaml
from flask import Flask, request, jsonify
from urllib.parse import urlparse

app = Flask(__name__)

STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

LEDGER = [
    {"id": "txn_1001", "pan": "4242424242424242", "amount": 4200, "currency": "USD", "status": "captured"},
    {"id": "txn_1002", "pan": "5555555555554444", "amount": 1899, "currency": "EUR", "status": "refunded"},
]

ALLOWED_DOMAINS = [
    "example.com",
    "httpbin.org"
]


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/tokenize", methods=["POST"])
def tokenize():
    payload = request.get_json(silent=True) or {}
    pan = payload.get("pan", "")
    token = "tok_" + hashlib.sha256(pan.encode()).hexdigest()[:24]
    return jsonify(token=token, last4=pan[-4:])


@app.route("/transactions")
def transactions():
    return jsonify(transactions=LEDGER)


@app.route("/import", methods=["POST"])
def import_config():
    try:
        config = yaml.safe_load(request.data)
        return jsonify(loaded=config)
    except yaml.YAMLError as e:
        return jsonify(error="Invalid YAML", details=str(e)), 400


@app.route("/fetch")
def fetch():
    url = request.args.get("url", "")

    if not url:
        return jsonify(error="URL is required"), 400

    parsed = urlparse(url)

    if parsed.scheme not in ["http", "https"]:
        return jsonify(error="Invalid URL scheme"), 400

    if parsed.hostname not in ALLOWED_DOMAINS:
        return jsonify(error="Domain not allowed"), 403

    try:
        resp = requests.get(url, timeout=5)
        return jsonify(
            status_code=resp.status_code,
            body=resp.text[:2048]
        )
    except Exception as e:
        return jsonify(error=str(e)), 500
    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
