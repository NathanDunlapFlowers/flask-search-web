from flask import Flask, request, jsonify
import requests
import os
import random
import sys
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

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
            "num": 10,
            "start": 0
        }

        print("Sending request to SerpAPI with params:", params)
        sys.stdout.flush()
        response = requests.get(search_url, params=params)
        print("SerpAPI response status:", response.status_code)
        sys.stdout.flush()

        serp_data = response.json()
        raw_results = serp_data.get("organic_results", [])
        print(f"Found {len(raw_results)} organic results")
        sys.stdout.flush()

        # Fallback: Try news_results if not enough organic results
        if len(raw_results) < num_results:
            news = serp_data.get("news_results", [])
            print(f"Found {len(news)} news results")
            sys.stdout.flush()
            raw_results.extend(news)

        # Remove duplicates based on URL
        seen = set()
        unique_results = []
        for r in raw_results:
            url = r.get("link") or r.get("url")
            if url and url not in seen:
                seen.add(url)
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
