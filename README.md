
# Flask Web Search API with SerpAPI for OpenAI Assistant

This Flask server handles a function call from OpenAI's Assistant and returns web search results using SerpAPI.

## Features
- Receives POST requests to `/search_web`
- Uses SerpAPI to perform a Google search
- Returns structured JSON with titles, links, and snippets

## Setup Instructions

1. Clone this repo and install dependencies:
    ```
    pip install -r requirements.txt
    ```

2. Create a `.env` file:
    ```
    cp .env.example .env
    ```

3. Add your SerpAPI key to the `.env` file.

4. Run the server:
    ```
    python server.py
    ```

5. (Optional) Expose your server with ngrok:
    ```
    ngrok http 5000
    ```

## Example Request Payload
```json
{
  "query": "latest AI trends 2025",
  "num_results": 3
}
```

## Example Response
```json
[
  {
    "title": "AI Trends 2025: What to Expect",
    "url": "https://example.com/ai-trends-2025",
    "snippet": "Discover the top AI advancements to watch in 2025..."
  },
  ...
]
```
