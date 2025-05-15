
from flask import Flask, request, jsonify
import requests
import os
import random
import sys
import sqlite3
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# Updated path for Render persistent disk
DB_FILE = "/var/data/sources.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS used_sources (
            id INTEGER PRIMARY KEY,
            domain TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

def is_new_domain(domain):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM used_sources WHERE domain=?", (domain,))
    exists = c.fetchone()
    conn.close()
    return not exists

def store_new_domain(domain):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO used_sources (domain) VALUES (?)", (domain,))
    conn.commit()
    conn.close()

init_db()

@app.route("/search_web", methods=["POST"])
def search_web():
    try:
        data = request.json
        print("Incoming data:", data)
        sys.stdout.flush()

        if not data or "query" not in data:
            return jsonify({"error": "Missing 'query' parameter"}), 400

        query = data["query"]
        num_results = int(data.get("num_results", 5))
        seed = int(data.get("randomizer", random.randint(0, 10000)))
        random.seed(seed)

        search_url = "https://serpapi.com/search"
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERPAPI_KEY,
            "num": 20,
            "start": 0
        }

        print("Sending request to SerpAPI with params:", params)
        sys.stdout.flush()
        response = requests.get(search_url, params=params)
        print("SerpAPI response status:", response.status_code)
        sys.stdout.flush()

        serp_data = response.json()
        raw_results = (
            serp_data.get("organic_results", []) +
            serp_data.get("news_results", []) +
            serp_data.get("top_stories", []) +
            serp_data.get("inline_videos", [])
        )
        print(f"Total raw results: {len(raw_results)}")
        sys.stdout.flush()

        seen = set()
        unique_results = []
        for r in raw_results:
            url = r.get("link") or r.get("url")
            if url:
                domain = urlparse(url).netloc
                if domain and domain not in seen and is_new_domain(domain):
                    seen.add(domain)
                    store_new_domain(domain)
                    unique_results.append(r)

        random.shuffle(unique_results)
        results = unique_results[:num_results]

        formatted = []
        for item in results:
            snippet = item.get("snippet", "") or item.get("description", "")
            highlights = item.get("snippet_highlighted_words", [])
            if highlights:
                highlighted_text = " ".join(highlights)
                snippet = f"{snippet} {highlighted_text}".strip()
            if not snippet and highlights:
                snippet = " ".join(highlights)

            formatted.append({
                "title": item.get("title") or item.get("source", {}).get("title", ""),
                "url": item.get("link") or item.get("url"),
                "snippet": snippet
            })

        print(f"Returning {len(formatted)} results")
        sys.stdout.flush()

        return jsonify({ "results": formatted })

    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print("ERROR:", traceback_str)
        sys.stdout.flush()
        return jsonify({"error": str(e), "trace": traceback_str}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
