import os
from flask import Flask, jsonify
from flask_cors import CORS
from .config import Settings
from .services.model import ModelService
from .api.routes import api_bp


def create_app() -> Flask:
    settings = Settings()
    app = Flask(__name__)
    app.config.update(
        FRONTEND_ORIGIN=settings.FRONTEND_ORIGIN,
        MAX_COMMENTS=settings.MAX_COMMENTS,
        MAX_SEQUENCE_LENGTH=settings.MAX_SEQUENCE_LENGTH,
    )

    CORS(app, resources={r"/api/*": {"origins": settings.FRONTEND_ORIGIN}})

    # Load model/tokenizer once at startup
    app.model_service = ModelService(
        model_path=settings.MODEL_PATH,
        tokenizer_path=settings.VECTORIZER_PATH,
        max_sequence_length=settings.MAX_SEQUENCE_LENGTH,
    )
    app.youtube_api_key = settings.YOUTUBE_API_KEY

    # Register API blueprint
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.get("/health")
    def health():
        return jsonify({
            "status": "ok",
            "model_loaded": app.model_service is not None,
            "max_sequence_length": app.config.get("MAX_SEQUENCE_LENGTH"),
        })

    return app 