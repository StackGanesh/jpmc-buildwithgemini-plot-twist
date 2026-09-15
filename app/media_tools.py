# app/media_tools.py
import json
import re
import urllib.parse
import urllib.request


def search_books(query: str, max_results: int = 3) -> str:
    """Searches Wikipedia for real book information, synopses, and details matching a search query.

    Args:
        query: Search term (e.g. book title, author name, or genre query like 'Dune Frank Herbert' or 'Project Hail Mary').
        max_results: Number of search results to return (default 3, max 5).

    Returns:
        A JSON string containing a list of books with title, snippet, and Wikipedia URL.
    """
    try:
        search_query = f"{query} novel book"
        encoded_query = urllib.parse.quote(search_query)
        limit = min(max(1, max_results), 5)
        url = (
            f"https://en.wikipedia.org/w/api.php?action=query&list=search"
            f"&srsearch={encoded_query}&format=json"
        )

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "PlotTwist-Agent/1.0 (contact@plottwist.app)"}
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        search_results = data.get("query", {}).get("search", [])
        if not search_results:
            return f"No book details found for query: '{query}'"

        results = []
        for item in search_results[:limit]:
            title = item.get("title", "")
            raw_snippet = item.get("snippet", "")
            # Remove HTML tags from snippet
            clean_snippet = re.sub(r"<[^>]+>", "", raw_snippet)
            clean_snippet = clean_snippet.replace("&quot;", '"').replace("&#039;", "'")

            page_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"

            results.append({
                "title": title,
                "snippet": clean_snippet,
                "url": page_url,
                "word_count": item.get("wordcount", 0),
            })

        return json.dumps(results, indent=2)

    except Exception as e:
        return f"Error executing book search: {str(e)}"
