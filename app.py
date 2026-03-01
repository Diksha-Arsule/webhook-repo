from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb+srv://Project2:8hRBmkm4AjDeZldv@cluster1.u2jzahm.mongodb.net/?appName=Cluster1")
db = client.github_events
collection = db.events


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event_type = request.headers.get("X-GitHub-Event")

    author = None
    from_branch = None
    to_branch = None
    request_id = None

    if event_type == "push":
        author = data["pusher"]["name"]
        to_branch = data["ref"].split("/")[-1]
        request_id = data["after"]
        action = "PUSH"

    elif event_type == "pull_request":
        author = data["pull_request"]["user"]["login"]
        from_branch = data["pull_request"]["head"]["ref"]
        to_branch = data["pull_request"]["base"]["ref"]
        request_id = str(data["pull_request"]["id"])

        if data["action"] == "closed" and data["pull_request"]["merged"]:
            action = "MERGE"
        else:
            action = "PULL_REQUEST"

    else:
        return jsonify({"msg": "ignored"}), 200

    document = {
        "request_id": request_id,
        "author": author,
        "action": action,
        "from_branch": from_branch,
        "to_branch": to_branch,
        "timestamp": datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
    }

    collection.insert_one(document)

    return jsonify({"msg": "stored"}), 200


@app.route("/events", methods=["GET"])
def get_events():
    events = list(collection.find().sort("_id", -1).limit(20))
    for e in events:
        e["_id"] = str(e["_id"])
    return jsonify(events)


if __name__ == "__main__":
    app.run(debug=True)