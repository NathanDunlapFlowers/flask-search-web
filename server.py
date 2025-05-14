
from flask import Flask, request, jsonify
import requests
import os
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
        
        search_url = "https://serpapi.com/search"
        params = {
            "engine": "google",
            "q": query,
            "api_key": os.getenv("SERPAPI_KEY"),
            "num": 10,
            "start": 0
        }
        
        response = requests.get(search_url, params=params)
        results = response.json().get("organic_results", [])[:num_results]

        formatted = []
        for item in results:
            # Start with the default snippet if available
            snippet = item.get("snippet", "")
        
            # Optionally append highlighted words
            highlights = item.get("snippet_highlighted_words", [])
            if highlights:
                highlighted_text = " ".join(highlights)
                snippet = f"{snippet} {highlighted_text}".strip()
        
            # Fallback in case snippet is missing but highlights exist
            if not snippet and highlights:
                snippet = " ".join(highlights)
        
            formatted.append({
                "title": item.get("title"),
                "url": item.get("link"),
                "snippet": snippet
            })

        return jsonify(formatted)

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
