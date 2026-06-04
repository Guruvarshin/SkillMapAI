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

import urllib.parse
from utils.helpers import slugify
from tools.youtube_tool import YouTubeTool

def run_video_hunter(topic_tree: dict, skill: str) -> dict:
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

    tool = YouTubeTool()
    results = {}

    for topic in topic_tree.get("topics", []):
        for subtopic in topic.get("subtopics", []):
            sub_id = subtopic.get("id", slugify(subtopic.get("name", "topic")))
            sub_name = subtopic.get("name", "")

            query = f"{skill} {sub_name} tutorial"

            try:
                video_json = tool._run(query=query, search_type="video")
                import json
                video_result = json.loads(video_json)
            except Exception:
                video_result = _fallback_video(query, sub_name, "video")

            try:
                playlist_json = tool._run(query=query, search_type="playlist")
                playlist_result = json.loads(playlist_json)
            except Exception:
                playlist_result = _fallback_video(query, sub_name, "playlist")

            results[sub_id] = {
                "video": video_result,
                "playlist": playlist_result,
            }

    return results

def _fallback_video(query: str, sub_name: str, vtype: str) -> dict:

    encoded = urllib.parse.quote_plus(query)
    return {
        "title": f"Search YouTube: {sub_name}",
        "url": f"https://www.youtube.com/results?search_query={encoded}",
        "channel": "",
        "type": vtype,
        "source": "search_url_fallback",
    }

def build_video_fallbacks(topic_tree: dict, skill: str) -> dict:
\
\
\
\

    fallbacks = {}
    for topic in topic_tree.get("topics", []):
        for sub in topic.get("subtopics", []):
            sub_id = sub.get("id", slugify(sub.get("name", "topic")))
            sub_name = sub.get("name", "")
            query = f"{skill} {sub_name} tutorial"
            encoded = urllib.parse.quote_plus(query)
            base = f"https://www.youtube.com/results?search_query={encoded}"
            fallbacks[sub_id] = {
                "video": {
                    "title": f"Search YouTube: {sub_name}",
                    "url": base,
                    "channel": "",
                    "type": "video",
                    "source": "search_url_fallback",
                },
                "playlist": {
                    "title": f"Search YouTube playlists: {sub_name}",
                    "url": base + "+playlist",
                    "channel": "",
                    "type": "playlist",
                    "source": "search_url_fallback",
                },
            }
    return fallbacks
