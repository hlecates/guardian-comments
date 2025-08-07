import re
from typing import List
from googleapiclient.discovery import build

_YT_RE = re.compile(r"(?:v=|/shorts/|/embed/|youtu\.be/)([A-Za-z0-9_-]{11})")


def extract_video_id(url: str) -> str:
    m = _YT_RE.search(url)
    if not m:
        raise ValueError("Invalid YouTube URL")
    return m.group(1)


def fetch_comments(api_key: str, video_id: str, max_comments: int = 300) -> List[str]:
    service = build("youtube", "v3", developerKey=api_key)
    comments: List[str] = []
    token = None
    while len(comments) < max_comments:
        req = service.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(100, max_comments - len(comments)),
            pageToken=token,
            textFormat="plainText",
            order="relevance",
        )
        resp = req.execute()
        for item in resp.get("items", []):
            top = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(top)
        token = resp.get("nextPageToken")
        if not token:
            break
    return comments 