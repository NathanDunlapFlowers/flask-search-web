
from flask import Flask, request, jsonify
import requests
import os
import random
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

@app.route("/search_web", methods=["POST"])
def search_web():
    try:
        data = request.json
        print("Incoming data:", data)

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
            "api_key": os.getenv("SERPAPI_KEY"),
            "num": 10,
            "start": 0
        }

        print("Sending request to SerpAPI with params:", params)
        response = requests.get(search_url, params=params)
        print("SerpAPI response status:", response.status_code)

        serp_data = response.json()
        print("Raw SerpAPI response keys:", serp_data.keys())

        raw_results = serp_data.get("organic_results", [])
        print(f"Found {len(raw_results)} organic results")

        # Shuffle and select up to num_results
        random.shuffle(raw_results)
        results = raw_results[:num_results]

        formatted = []
        for item in results:
            snippet = item.get("snippet", "")
            highlights = item.get("snippet_highlighted_words", [])
            if highlights:
                highlighted_text = " ".join(highlights)
                snippet = f"{snippet} {highlighted_text}".strip()
            if not snippet and highlights:
                snippet = " ".join(highlights)

            formatted.append({
                "title": item.get("title"),
                "url": item.get("link"),
                "snippet": snippet
            })

        if len(results) < num_results:
            print(f"⚠️ Only {len(results)} results returned by SerpAPI (expected {num_results})")

        return jsonify(formatted)

    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print("ERROR:", traceback_str)
        return jsonify({"error": str(e), "trace": traceback_str}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
