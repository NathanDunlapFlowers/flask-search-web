from flask import Flask, request, jsonify
import requests
import os
import random
import sys
import sqlite3
from urllib.parse import urlparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
DEBUG_ADMIN_KEY = os.getenv("DEBUG_ADMIN_KEY")
DB_FILE = "/var/data/sources.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS used_sources (
            id INTEGER PRIMARY KEY,
            url TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

def is_new_url(url):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM used_sources WHERE url=?", (url,))
    exists = c.fetchone()
    conn.close()
    return not exists

def store_url(url):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO used_sources (url) VALUES (?)", (url,))
    conn.commit()
    conn.close()

def is_ai_related(title, snippet):
    keywords = [
        "ai", "artificial intelligence", "machine learning", "deep learning",
        "generative ai", "gen ai", "chatgpt", "llm", "openai", "neural network"
    ]
    text = f"{title} {snippet}".lower()
    return any(k in text for k in keywords)

def get_serp_results(query, tbs_filter=None):
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 20,
        "start": 0
    }
    if tbs_filter:
        params["tbs"] = tbs_filter

    response = requests.get("https://serpapi.com/search", params=params)
    if response.status_code != 200:
        return []

    data = response.json()
    return (
        data.get("organic_results", []) +
        data.get("news_results", []) +
        data.get("top_stories", []) +
        data.get("inline_videos", [])
    )

init_db()

@app.before_request
def protect_debug_routes():
    if request.path.startswith("/debug"):
        key = request.headers.get("X-Admin-Key")
        if key != DEBUG_ADMIN_KEY:
            return jsonify(Error: Unauthorized), 403

@app.route("/search_web", methods=["POST"])
def search_web():
    try:
        data = request.json
        if not data or "query" not in data:
            return jsonify({"error": "Missing 'query' parameter"}), 400

        query = data["query"]
        num_results = int(data.get("num_results", 5))
        seed = int(data.get("randomizer", random.randint(0, 10000)))
        random.seed(seed)

        all_raw_results = []
        for tbs in ["qdr:d", "qdr:w", "qdr:m", "qdr:y"]:
            results = get_serp_results(query, tbs)
            all_raw_results.extend(results)
            if len(all_raw_results) >= num_results:
                break

        seen_urls = set()
        candidate_results = []
        for r in all_raw_results:
            url = r.get("link") or r.get("url")
            if not url or not is_new_url(url):
                continue
            if url in seen_urls:
                continue

            title = r.get("title", "")
            snippet = r.get("snippet", "") or r.get("description", "")

            if not is_ai_related(title, snippet):
                continue

            seen_urls.add(url)
            candidate_results.append((url, title, snippet))

        random.shuffle(candidate_results)
        final = candidate_results[:num_results]

        formatted = []
        for url, title, snippet in final:
            store_url(url)
            formatted.append({
                "title": title,
                "url": url,
                "snippet": snippet
            })

        return jsonify({ "results": formatted })

    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print("ERROR:", traceback_str)
        sys.stdout.flush()
        return jsonify({"error": str(e), "trace": traceback_str}), 500

@app.route("/debug/list-db", methods=["GET"])
def list_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT url FROM used_sources ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return jsonify({"entries": [r[0] for r in rows]})

@app.route("/debug/clear-db", methods=["POST"])
def clear_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM used_sources")
    conn.commit()
    conn.close()
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
