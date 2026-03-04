from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from datetime import datetime
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------
# MongoDB Connection (Safe Setup)
# -------------------------------

# Get MongoDB URI from environment variable
# For local development: use localhost fallback
# For production: MUST set MONGODB_URI environment variable
mongo_uri = os.environ.get("MONGODB_URI") or "mongodb://localhost:27017/github_webhook"
is_production = os.environ.get("FLASK_ENV") == "production"

client = None
db = None
collection = None

try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    # Verify the connection
    client.admin.command('ping')
    db = client.github_webhook
    collection = db.events
    logger.info("✓ MongoDB connection successful")
except (ServerSelectionTimeoutError, ConnectionFailure) as e:
    if is_production:
        logger.error(f"✗ MongoDB connection failed in production: {e}")
        raise ValueError(f"Cannot connect to MongoDB: {e}")
    else:
        logger.warning(f"⚠ MongoDB connection failed (development mode): {e}")
        logger.info("Running in memory mode - data will not persist")


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
    try:
        data = request.get_json(silent=True)
        event_type = request.headers.get("X-GitHub-Event")

        if not data or not event_type:
            logger.warning("Invalid webhook request: missing data or event type")
            return jsonify({"error": "Invalid webhook request"}), 400

        author = None
        from_branch = None
        to_branch = None
        request_id = None
        action = None

        # PUSH EVENT
        if event_type == "push":
            pusher = data.get("pusher", {})
            if not pusher:
                logger.warning("PUSH event missing pusher information")
                return jsonify({"error": "Invalid push event"}), 400
            
            author = pusher.get("name")
            to_branch = data.get("ref", "").split("/")[-1]
            request_id = data.get("after")
            action = "PUSH"

        # PULL REQUEST EVENT
        elif event_type == "pull_request":
            pr = data.get("pull_request", {})
            if not pr:
                logger.warning("PULL_REQUEST event missing PR data")
                return jsonify({"error": "Invalid pull request event"}), 400

            author = pr.get("user", {}).get("login")
            from_branch = pr.get("head", {}).get("ref")
            to_branch = pr.get("base", {}).get("ref")
            request_id = str(pr.get("id"))

            if data.get("action") == "closed" and pr.get("merged"):
                action = "MERGE"
            else:
                action = "PULL_REQUEST"

        else:
            # Ignore unsupported events
            logger.info(f"Event type '{event_type}' ignored")
            return jsonify({"msg": "Event ignored"}), 200

        # Validate extracted data
        if not author or not request_id or not action:
            logger.warning(f"Incomplete event data: author={author}, request_id={request_id}, action={action}")
            return jsonify({"error": "Incomplete event data"}), 400

        document = {
            "request_id": request_id,
            "author": author,
            "action": action,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC"),
            "event_type": event_type
        }

        if collection is not None:
            collection.insert_one(document)
            logger.info(f"✓ Event stored: {action} by {author}")
        else:
            logger.warning(f"⚠ MongoDB not available - event not stored: {action} by {author}")

        return jsonify({"msg": "Event received" if collection else "Event received (not stored)"}), 200

    except Exception as e:
        logger.error(f"✗ Webhook error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# -------------------------------
# Fetch Events for UI
# -------------------------------
@app.route("/events", methods=["GET"])
def get_events():
    try:
        if collection is None:
            logger.warning("Database not available")
            return jsonify([]), 200
        
        limit = request.args.get("limit", 20, type=int)
        limit = min(limit, 100)  # Cap at 100 to prevent abuse
        
        events = list(collection.find().sort("_id", -1).limit(limit))
        for event in events:
            event["_id"] = str(event["_id"])
        
        logger.info(f"✓ Retrieved {len(events)} events")
        return jsonify(events), 200
    except Exception as e:
        logger.error(f"✗ Error fetching events: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch events"}), 500


# -------------------------------
# Health Check Endpoint
# -------------------------------
@app.route("/health", methods=["GET"])
def health():
    try:
        if client is not None:
            client.admin.command('ping')
            return jsonify({"status": "healthy", "database": "connected"}), 200
        else:
            return jsonify({"status": "healthy", "database": "disconnected"}), 200
    except Exception as e:
        logger.error(f"✗ Health check failed: {e}")
        return jsonify({"status": "unhealthy", "database": "disconnected"}), 503


# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"✗ Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
















