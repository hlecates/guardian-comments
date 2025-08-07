from flask import Blueprint, current_app, request, jsonify
from ..services.youtube import extract_video_id, fetch_comments


api_bp = Blueprint("api", __name__)


@api_bp.post("/score")
def score():
    data = request.get_json(silent=True) or {}
    texts = data.get("texts")
    if not isinstance(texts, list) or not all(isinstance(t, str) for t in texts):
        return jsonify({"error": "texts must be a list of strings"}), 400
    scores = current_app.model_service.score(texts)
    agg = {"mean_toxicity": float(sum(s.get("toxic", 0.0) for s in scores) / max(len(scores), 1))}
    return jsonify({"scores": scores, "aggregate": agg})


@api_bp.post("/youtube/score")
def youtube_score():
    api_key = current_app.youtube_api_key
    if not api_key:
        return jsonify({"error": "Missing YOUTUBE_API_KEY"}), 500
    data = request.get_json(silent=True) or {}
    url = data.get("url")
    max_comments = int(data.get("max_comments", current_app.config["MAX_COMMENTS"]))
    if not isinstance(url, str) or not url:
        return jsonify({"error": "url is required"}), 400
    try:
        vid = extract_video_id(url)
        comments = fetch_comments(api_key, vid, max_comments=max_comments)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    if not comments:
        return jsonify({"scores": [], "aggregate": {"mean_toxicity": 0.0}})
    scores = current_app.model_service.score(comments)
    agg = {"mean_toxicity": float(sum(s.get("toxic", 0.0) for s in scores) / len(scores))}
    return jsonify({"scores": scores, "aggregate": agg}) 