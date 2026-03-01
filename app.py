from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)

# -------------------------------
# MongoDB Connection (Safe Setup)
# -------------------------------

mongo_uri = os.environ.get("mongodb+srv://Project2:8hRBmkm4AjDeZldv@cluster1.u2jzahm.mongodb.net/?appName=Cluster1")

if not mongo_uri:
    raise Exception("MONGO_URI environment variable not set")

client = MongoClient(mongo_uri)
db = client.github_events
collection = db.events


# -------------------------------
# Home Route
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -------------------------------
# Webhook Receiver
# -------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event_type = request.headers.get("X-GitHub-Event")

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    author = None
    from_branch = None
    to_branch = None
    request_id = None
    action = None

    # PUSH EVENT
    if event_type == "push":
        author = data.get("pusher", {}).get("name")
        to_branch = data.get("ref", "").split("/")[-1]
        request_id = data.get("after")
        action = "PUSH"

    # PULL REQUEST EVENT
    elif event_type == "pull_request":
        pr = data.get("pull_request", {})

        author = pr.get("user", {}).get("login")
        from_branch = pr.get("head", {}).get("ref")
        to_branch = pr.get("base", {}).get("ref")
        request_id = str(pr.get("id"))

        if data.get("action") == "closed" and pr.get("merged"):
            action = "MERGE"
        else:
            action = "PULL_REQUEST"

    else:
        return jsonify({"msg": "Event ignored"}), 200

    document = {
        "request_id": request_id,
        "author": author,
        "action": action,
        "from_branch": from_branch,
        "to_branch": to_branch,
        "timestamp": datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
    }

    collection.insert_one(document)

    return jsonify({"msg": "Event stored"}), 200


# -------------------------------
# Fetch Events for UI
# -------------------------------
@app.route("/events", methods=["GET"])
def get_events():
    events = list(collection.find().sort("_id", -1).limit(20))
    for e in events:
        e["_id"] = str(e["_id"])
    return jsonify(events)


# -------------------------------
# Local Development Only
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)

















# from flask import Flask, request, jsonify, render_template
# from pymongo import MongoClient
# from datetime import datetime
# import os

# app = Flask(__name__)

# # MongoDB connection
# client = MongoClient(os.environ.get("MONGO_URI"))
# db = client.github_events
# collection = db.events


# @app.route("/")
# def home():
#     return render_template("index.html")


# @app.route("/webhook", methods=["POST"])
# def webhook():
#     data = request.json
#     event_type = request.headers.get("X-GitHub-Event")

#     author = None
#     from_branch = None
#     to_branch = None
#     request_id = None

#     if event_type == "push":
#         author = data["pusher"]["name"]
#         to_branch = data["ref"].split("/")[-1]
#         request_id = data["after"]
#         action = "PUSH"

#     elif event_type == "pull_request":
#         author = data["pull_request"]["user"]["login"]
#         from_branch = data["pull_request"]["head"]["ref"]
#         to_branch = data["pull_request"]["base"]["ref"]
#         request_id = str(data["pull_request"]["id"])

#         if data["action"] == "closed" and data["pull_request"]["merged"]:
#             action = "MERGE"
#         else:
#             action = "PULL_REQUEST"

#     else:
#         return jsonify({"msg": "ignored"}), 200

#     document = {
#         "request_id": request_id,
#         "author": author,
#         "action": action,
#         "from_branch": from_branch,
#         "to_branch": to_branch,
#         "timestamp": datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
#     }

#     collection.insert_one(document)

#     return jsonify({"msg": "stored"}), 200


# @app.route("/events", methods=["GET"])
# def get_events():
#     events = list(collection.find().sort("_id", -1).limit(20))
#     for e in events:
#         e["_id"] = str(e["_id"])
#     return jsonify(events)


# if __name__ == "__main__":
#     app.run(debug=True)