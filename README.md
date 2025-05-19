# Flask AI News Scraper

This Flask app provides an API to retrieve AI-related web search results using SerpAPI and stores previously used URLs in a local SQLite database to avoid repetition. It supports filtering by time (day, week, month, year) and only keeps results that are AI-relevant based on title/snippet content.

## Features

- Retrieves fresh Google search results via SerpAPI
- Prioritizes content from today, then this week, month, and year
- Deduplicates results based on URLs
- Filters for articles relevant to AI (based on keyword match)
- Persists used URLs with a SQLite database on disk
- Includes `/debug` endpoints to view and clear stored URLs

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

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create `.env` file

Copy the `.env.example` and add your [SerpAPI key](https://serpapi.com/):

```bash
cp .env.example .env
```

### 3. Run the server

```bash
python server.py
```

## Deployment

Recommended for deployment on [Render](https://render.com/), with persistent disk mounted to `/var/data`.

---

## License

MIT
