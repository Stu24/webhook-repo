from flask import Flask, request, render_template, jsonify
from pymongo import MongoClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

client = MongoClient(os.getenv("MONGO_URI"))
db = client["webhook_db"]
collection = db["events"]

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("📦 Raw webhook data:", data)  # Debug print
    event_type = request.headers.get('X-GitHub-Event')
    print("🔔 Event type received:", event_type)  # Debug print

    author = data.get('sender', {}).get('login', 'Unknown')
    timestamp = datetime.now(timezone.utc)

    if event_type == 'push':
        to_branch = data.get('ref', '').split('/')[-1]
        print(f"💾 Saving push by {author} to branch {to_branch}")
        collection.insert_one({
            "author": author,
            "action_type": "push",
            "to_branch": to_branch,
            "timestamp": timestamp
        })

    elif event_type == 'pull_request':
        pr = data.get('pull_request', {})
        from_branch = pr.get('head', {}).get('ref', 'unknown')
        to_branch = pr.get('base', {}).get('ref', 'unknown')
        print(f"💾 Saving PR by {author} from {from_branch} to {to_branch}")
        collection.insert_one({
            "author": author,
            "action_type": "pull_request",
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        })

    else:
        print("⚠️ Unknown or unsupported event type:", event_type)

    return "Event received", 200

@app.route('/events')
def events():
    data = list(collection.find().sort("timestamp", -1))
    for d in data:
        d["_id"] = str(d["_id"])  # Convert ObjectId to string
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
