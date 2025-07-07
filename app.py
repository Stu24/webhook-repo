from flask import Flask, request, render_template, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

client = MongoClient("mongodb+srv://stuti:iOeETKNtlYtsmu97@python.xwjox7c.mongodb.net/?retryWrites=true&w=majority&appName=Python")  # Replace this
db = client["webhook_db"]
collection = db["events"]

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')

    author = data['sender']['login']
    timestamp = datetime.utcnow()

    if event_type == 'push':
        to_branch = data['ref'].split('/')[-1]
        collection.insert_one({
            "author": author,
            "action_type": "push",
            "to_branch": to_branch,
            "timestamp": timestamp
        })

    elif event_type == 'pull_request':
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        collection.insert_one({
            "author": author,
            "action_type": "pull_request",
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        })

    return "Event received", 200

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/events')
def events():
    data = list(collection.find().sort("timestamp", -1))
    for d in data:
        d["_id"] = str(d["_id"])
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
