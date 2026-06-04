import os
import json
import urllib.parse
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from dotenv import load_dotenv
load_dotenv()
class YouTubeSearchInput(BaseModel):
    query: str = Field(
        description="Search query for YouTube, e.g. 'React hooks tutorial beginner'"
    )
    search_type: str = Field(
        default="video",
        description="Type of result to find: 'video' for a single tutorial, 'playlist' for a course playlist"
    )
class YouTubeTool(BaseTool):
    name: str = "youtube_search"
    description: str = (
        "Search YouTube for tutorial videos and playlists. "
        "Use search_type='video' to find the best single tutorial video. "
        "Use search_type='playlist' to find the best full course playlist. "
        "Returns JSON with title, url, channel, and type fields."
    )
    args_schema: Type[BaseModel] = YouTubeSearchInput
    def _run(self, query: str, search_type: str = "video") -> str:
        result = self._search_youtube_api(query, search_type)
        if result:
            return json.dumps(result)
        result = self._search_via_tavily(query, search_type)
        if result:
            return json.dumps(result)
        return json.dumps(self._fallback_search_url(query, search_type))
    def _search_youtube_api(self, query: str, search_type: str) -> dict | None:
        api_key = os.environ.get("YOUTUBE_API_KEY", "").strip()
        if not api_key or api_key == "your_youtube_api_key_here":
            return None                                       
        try:
            from googleapiclient.discovery import build
            from googleapiclient.errors import HttpError
            youtube = build(
                "youtube", "v3",
                developerKey=api_key,
                cache_discovery=False,
            )
            api_type = "playlist" if search_type == "playlist" else "video"
            enhanced_query = f"{query} tutorial" if "tutorial" not in query.lower() else query
            response = youtube.search().list(
                q=enhanced_query,
                type=api_type,
                part="snippet",
                maxResults=3,                                        
                relevanceLanguage="en",                          
                safeSearch="moderate",
                videoDuration="medium" if api_type == "video" else None,
            ).execute()
            items = response.get("items", [])
            if not items:
                return None
            item = items[0]
            snippet = item.get("snippet", {})
            item_id = item.get("id", {})
            if api_type == "video":
                video_id = item_id.get("videoId", "")
                if not video_id:
                    return None
                url = f"https://www.youtube.com/watch?v={video_id}"
            else:
                playlist_id = item_id.get("playlistId", "")
                if not playlist_id:
                    return None
                url = f"https://www.youtube.com/playlist?list={playlist_id}"
            return {
                "title": snippet.get("title", "YouTube Tutorial"),
                "url": url,
                "channel": snippet.get("channelTitle", ""),
                "type": search_type,
                "source": "youtube_api",
            }
        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str:
                print(f"[YouTubeTool] API quota exceeded — falling back to Tavily")
            else:
                print(f"[YouTubeTool] API error: {e} — falling back to Tavily")
            return None
    def _search_via_tavily(self, query: str, search_type: str) -> dict | None:
        api_key = os.environ.get("TAVILY_API_KEY", "").strip()
        if not api_key or api_key == "your_tavily_api_key_here":
            return None
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=api_key)
            if search_type == "playlist":
                search_query = f"site:youtube.com/playlist {query} tutorial course"
            else:
                search_query = f"site:youtube.com/watch {query} tutorial"
            results = client.search(
                query=search_query,
                max_results=3,
                search_depth="basic",                                               
            )
            for result in results.get("results", []):
                url = result.get("url", "")
                if "youtube.com/watch?v=" in url or "youtube.com/playlist?list=" in url:
                    title = result.get("title", "YouTube Tutorial")
                    title = title.replace(" - YouTube", "").strip()
                    return {
                        "title": title,
                        "url": url,
                        "channel": "",                                        
                        "type": search_type,
                        "source": "tavily_fallback",
                    }
            return None                                            
        except Exception as e:
            print(f"[YouTubeTool] Tavily fallback error: {e}")
            return None
    def _fallback_search_url(self, query: str, search_type: str) -> dict:
        search_query = f"{query} tutorial"
        if search_type == "playlist":
            search_query += " full course playlist"
        encoded = urllib.parse.quote_plus(search_query)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        return {
            "title": f"Search YouTube: {query}",
            "url": url,
            "channel": "",
            "type": search_type,
            "source": "search_url_fallback",
        }
def get_youtube_tool() -> YouTubeTool:
    return YouTubeTool()
