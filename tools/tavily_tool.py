\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\

import os
import json
import urllib.parse
from typing import Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from dotenv import load_dotenv

load_dotenv()

class TavilySearchInput(BaseModel):

    query: str = Field(
        description=(
            "Search query. Be specific for best results. "
            "Examples: "
            "'React hooks useState tutorial freeCodeCamp certificate', "
            "'Python decorators Udemy course price rating', "
            "'async await JavaScript MDN documentation'"
        )
    )
    search_type: str = Field(
        default="resource",
        description=(
            "Type of resource to find: "
            "'resource' for text resources (docs, articles), "
            "'free_course' for free courses with certificates, "
            "'paid_course' for paid courses with prices"
        )
    )

class TavilyTool(BaseTool):
\
\
\
\
\
\

    name: str = "web_search"
    description: str = (
        "Search the web for learning resources. "
        "Use search_type='resource' for docs and tutorials. "
        "Use search_type='free_course' for free courses with certificates. "
        "Use search_type='paid_course' for paid courses with prices and ratings. "
        "Returns JSON with title, url, and relevant metadata."
    )
    args_schema: Type[BaseModel] = TavilySearchInput

    def _run(self, query: str, search_type: str = "resource") -> str:
\
\
\
\
\
\
\
\
\

        enhanced_query = self._enhance_query(query, search_type)

        result = self._search_tavily(enhanced_query, search_type)
        if result:
            return json.dumps(result)

        return json.dumps(self._fallback_google_url(query, search_type))

    def _enhance_query(self, query: str, search_type: str) -> str:
\
\
\
\
\

        if search_type == "free_course":

            return f"{query} free course certificate Coursera OR edX OR freeCodeCamp OR Google OR Kaggle"

        elif search_type == "paid_course":

            return f"{query} course Udemy site:udemy.com"

        else:

            return query

    def _search_tavily(self, query: str, search_type: str) -> dict | None:
\
\
\
\
\
\
\
\
\
\
\
\
\

        api_key = os.environ.get("TAVILY_API_KEY", "").strip()
        if not api_key or api_key == "your_tavily_api_key_here":
            return None

        try:
            from tavily import TavilyClient

            client = TavilyClient(api_key=api_key)

            response = client.search(
                query=query,
                max_results=5,                                     
                search_depth="basic",                               
                include_answer=False,                                 
            )

            results = response.get("results", [])
            if not results:
                return None

            best = self._pick_best_result(results, search_type)
            if not best:
                return None

            return self._format_result(best, search_type)

        except Exception as e:
            print(f"[TavilyTool] Search error: {e}")
            return None

    def _pick_best_result(self, results: list, search_type: str) -> dict | None:
\
\
\
\
\
\
\
\
\
\
\
\

        if search_type == "paid_course":

            for r in results:
                if "udemy.com" in r.get("url", ""):
                    return r

            for r in results:
                url = r.get("url", "")
                if any(p in url for p in ["pluralsight.com", "frontendmasters.com", "skillshare.com"]):
                    return r

        elif search_type == "free_course":

            preferred = [
                "coursera.org", "edx.org", "freecodecamp.org",
                "kaggle.com", "developers.google.com", "learn.microsoft.com",
            ]
            for platform in preferred:
                for r in results:
                    if platform in r.get("url", ""):
                        return r

        else:                                   

            skip_domains = ["udemy.com", "coursera.org", "edx.org", "amazon.com"]
            for r in results:
                url = r.get("url", "")
                if not any(d in url for d in skip_domains):
                    return r

        return results[0] if results else None

    def _format_result(self, result: dict, search_type: str) -> dict:
\
\
\
\
\
\
\
\
\

        title = result.get("title", "Resource").replace(" - YouTube", "").strip()
        url = result.get("url", "")
        content = result.get("content", "")

        if search_type == "paid_course":

            price = self._extract_price(content)
            rating = self._extract_rating(content)
            platform = self._detect_platform(url)
            return {
                "name": title,
                "platform": platform,
                "url": url,
                "price": price,
                "rating": rating,
                "source": "tavily",
            }

        elif search_type == "free_course":
            platform = self._detect_platform(url)

            cert_platforms = ["freecodecamp.org", "kaggle.com", "developers.google.com"]
            certificate = any(p in url for p in cert_platforms)
            return {
                "name": title,
                "platform": platform,
                "url": url,
                "certificate": certificate,
                "source": "tavily",
            }

        else:            
            resource_type = self._detect_resource_type(url, title)
            return {
                "title": title,
                "url": url,
                "type": resource_type,
                "source": "tavily",
            }

    def _extract_price(self, content: str) -> str:

        import re
        if not content:
            return "~$15"

        match = re.search(r"\$(\d+(?:\.\d{2})?)", content)
        if match:
            amount = float(match.group(1))
            return f"${int(amount)}" if amount == int(amount) else f"${amount:.2f}"
        return "~$15"                             

    def _extract_rating(self, content: str) -> str:

        import re
        if not content:
            return ""

        match = re.search(r"(\d\.\d)\s*(?:out of 5|stars?|rating|/5)?", content)
        return match.group(1) if match else ""

    def _detect_platform(self, url: str) -> str:

        platform_map = {
            "udemy.com": "Udemy",
            "coursera.org": "Coursera",
            "edx.org": "edX",
            "freecodecamp.org": "freeCodeCamp",
            "kaggle.com": "Kaggle",
            "pluralsight.com": "Pluralsight",
            "frontendmasters.com": "Frontend Masters",
            "developers.google.com": "Google",
            "learn.microsoft.com": "Microsoft Learn",
            "linkedin.com/learning": "LinkedIn Learning",
        }
        for domain, name in platform_map.items():
            if domain in url:
                return name

        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except Exception:
            return "Online"

    def _detect_resource_type(self, url: str, title: str) -> str:

        url_lower = url.lower()
        title_lower = title.lower()
        if "docs." in url_lower or "/docs/" in url_lower or "documentation" in title_lower:
            return "documentation"
        if "blog" in url_lower or "blog" in title_lower:
            return "blog"
        if "guide" in title_lower or "tutorial" in title_lower:
            return "tutorial"
        return "article"

    def _fallback_google_url(self, query: str, search_type: str) -> dict:
\
\
\
\
\

        enhanced = query
        if search_type == "free_course":
            enhanced += " free course certificate"
        elif search_type == "paid_course":
            enhanced += " Udemy course"

        encoded = urllib.parse.quote_plus(enhanced)
        url = f"https://www.google.com/search?q={encoded}"

        if search_type == "paid_course":
            return {
                "name": f"Search for: {query}",
                "platform": "Search",
                "url": url,
                "price": "~$15",
                "rating": "",
                "source": "google_fallback",
            }
        elif search_type == "free_course":
            return {
                "name": f"Search for: {query}",
                "platform": "Search",
                "url": url,
                "certificate": False,
                "source": "google_fallback",
            }
        else:
            return {
                "title": f"Search for: {query}",
                "url": url,
                "type": "article",
                "source": "google_fallback",
            }

def get_tavily_tool() -> TavilyTool:
\
\
\
\
\
\

    return TavilyTool()
