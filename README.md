# Flask AI News Scraper

This Flask app provides an API to retrieve AI-related web search results using SerpAPI and stores previously used URLs in a local SQLite database to avoid repetition. It supports filtering by time (day, week, month, year) and only keeps results that are AI-relevant based on title/snippet content.

## Features

- Retrieves fresh Google search results via SerpAPI
- Prioritizes content from today, then this week, month, and year
- Deduplicates results based on URLs
- Filters for articles relevant to AI (based on keyword match)
- Persists used URLs with a SQLite database on disk
- Includes `/debug` endpoints to view and clear stored URLs

---

## Endpoints

### `POST /search_web`
Fetches and returns AI-related articles.

**Body:**
```json
{
  "query": "AI trends May 2025",
  "num_results": 5,
  "randomizer": 1234
}
```

**Returns:**
```json
{
  "results": [
    {
      "title": "...",
      "url": "...",
      "snippet": "..."
    }
  ]
}
```

### `GET /debug/list-db`
Returns a list of all stored URLs.

### `POST /debug/clear-db`
Clears the stored URL history.

---

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/yourusername/flask-ai-news.git
cd flask-ai-news
pip install -r requirements.txt
```

### 2. Create your `.env` file

Copy the template:

```bash
cp .env.example .env
```

And add your [SerpAPI key](https://serpapi.com/).

---

## Deployment

This app is designed for simple deployment using [Render](https://render.com/).

A preconfigured `render.yaml` file is included, which sets up:
- The Flask web service
- A 1 GB persistent disk at `/var/data`
- Environment variable for `SERPAPI_KEY`
- `autoDeploy: false` (you control when to deploy)

Just connect your repo to Render and it will auto-detect the `render.yaml`.

---

## Project Structure

```text
.
├── server.py            # Main Flask app
├── requirements.txt     # Python dependencies
├── .env.example         # Template for API key
├── .gitignore           # Ignore compiled/env/db files
├── render.yaml          # Render deployment configuration
├── LICENSE              # MIT license
└── README.md            # You're reading it
```

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
