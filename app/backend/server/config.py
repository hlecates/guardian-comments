import os
from dotenv import load_dotenv, find_dotenv

# Auto-load .env from project root or nearest parent
load_dotenv(find_dotenv())


class Settings:
    MODEL_PATH: str
    VECTORIZER_PATH: str
    MAX_SEQUENCE_LENGTH: int
    YOUTUBE_API_KEY: str
    FRONTEND_ORIGIN: str
    MAX_COMMENTS: int

    def __init__(self):
        self.MODEL_PATH = os.getenv("MODEL_PATH", "models/toxicity.keras")
        self.VECTORIZER_PATH = os.getenv("VECTORIZER_PATH", "models/tokenizer.pckl")
        self.MAX_SEQUENCE_LENGTH = int(os.getenv("MAX_SEQUENCE_LENGTH", "200"))
        self.YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
        self.FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
        self.MAX_COMMENTS = int(os.getenv("MAX_COMMENTS", "300")) 