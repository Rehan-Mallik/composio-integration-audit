import requests

from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
    )
}


def fetch_page(url: str, timeout: int = 15) -> dict:
    """
    Fetch a webpage and extract its readable text.
    """

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=timeout,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        for element in soup(
            ["script", "style", "noscript"]
        ):
            element.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True,
        )

        return {
            "success": True,
            "url": url,
            "status_code": response.status_code,
            "title": soup.title.string.strip()
            if soup.title and soup.title.string
            else "",
            "text": text,
        }

    except requests.RequestException as exc:
       return {
    "success": False,
    "url": url,
    "status_code": (
        exc.response.status_code
        if exc.response is not None
        else None
    ),
    "error": str(exc),
    "text": "",
}


if __name__ == "__main__":
    result = fetch_page(
        "https://developer.github.com/"
    )

    print("Success:", result["success"])
    print("Status:", result.get("status_code"))
    print("Title:", result.get("title"))
    print("Characters:", len(result.get("text", "")))
