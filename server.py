
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
            snippet = item.get("snippet", "")
            
            # Try to append rich info if available
            if "rich_snippet" in item:
                snippet += " " + str(item["rich_snippet"])
            elif "about_this_result" in item:
                snippet += " " + item["about_this_result"].get("source", "")
        
            formatted.append({
                "title": item.get("title"),
                "url": item.get("link"),
                "snippet": snippet.strip()
            })

        return jsonify(formatted)

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
