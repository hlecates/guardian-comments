# Guardian Comments - Toxicity Analysis System

An AI-powered system for analyzing toxicity in YouTube comments using machine learning. This system can be used as a command-line tool, web API, or integrated into web applications.

## Features

- **Toxicity Detection**: Analyze comments for multiple types of toxicity (toxic, severe_toxic, obscene, threat, insult, identity_hate)
- **YouTube Integration**: Extract and analyze comments directly from YouTube videos using the YouTube Data API
- **Web API**: RESTful API with FastAPI for easy integration into web applications
- **Command Line Interface**: Full-featured CLI for batch processing and single comment analysis
- **Web Frontend**: Beautiful HTML interface for interactive analysis
- **Flexible Deployment**: Can be deployed as a standalone service or integrated into existing applications

## Quick Start

### Prerequisites

- Python 3.8+
- YouTube Data API v3 key (for YouTube functionality)
- Pre-trained toxicity model and vectorizer files

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd guardian-comments
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your YouTube API key and other settings
   ```

4. **Place your model files in the model directory**
   - `toxicity.h5` - Trained Keras model
   - `vectorizer.pkl` - Text vectorizer

### Usage

#### Web Service

Start the FastAPI web service:

```bash
# Using the main application
python model/main.py web --port 8000

# Or directly with uvicorn
cd model
uvicorn web_service:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

#### Command Line Interface

**Analyze a YouTube video:**
```bash
python model/main.py youtube "https://www.youtube.com/watch?v=VIDEO_ID" --max-comments 100
```

**Analyze a single comment:**
```bash
python model/main.py comment "This is a test comment"
```

**Batch analysis with custom settings:**
```bash
python model/main.py youtube "https://youtu.be/VIDEO_ID" \
  --max-comments 50 \
  --threshold 0.6 \
  --order time \
  --output results.json
```

#### Web Frontend

Open `model/example_frontend.html` in your browser (make sure the API server is running).

## API Documentation

### Endpoints

#### `POST /analyze/youtube`
Analyze YouTube video comments.

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "max_comments": 100,
  "threshold": 0.5,
  "order": "relevance"
}
```

**Response:**
```json
{
  "video_info": {
    "title": "Video Title",
    "channel_title": "Channel Name",
    "view_count": 1000000
  },
  "analysis_summary": {
    "total_comments": 100,
    "toxic_comments": 15,
    "toxicity_percentage": 15.0,
    "average_toxicity_score": 0.234
  },
  "comments": [
    {
      "comment_id": "comment_id",
      "text": "Comment text",
      "author": "Author Name",
      "toxicity_score": 0.8,
      "is_toxic": true,
      "toxicity_categories": {
        "toxic": {"probability": 0.8, "is_toxic": true},
        "insult": {"probability": 0.3, "is_toxic": false}
      }
    }
  ]
}
```

#### `POST /analyze/comment`
Analyze a single comment.

**Request Body:**
```json
{
  "text": "Comment to analyze",
  "threshold": 0.5
}
```

#### `GET /analyze/youtube/{video_id}`
Analyze YouTube video by ID with query parameters.

**Query Parameters:**
- `max_comments`: Maximum comments to analyze (1-1000)
- `threshold`: Toxicity threshold (0.0-1.0)
- `order`: Comment order (`time` or `relevance`)

#### `GET /health`
Check service health status.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | Required for YouTube functionality |
| `MODEL_PATH` | Path to toxicity model file | `toxicity.h5` |
| `VECTORIZER_PATH` | Path to vectorizer file | `vectorizer.pkl` |
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |

### YouTube API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the YouTube Data API v3
4. Create credentials (API key)
5. Set the `YOUTUBE_API_KEY` environment variable

## Architecture

```
guardian-comments/
├── model/
│   ├── predict_toxicity.py    # Core toxicity prediction
│   ├── youtube_api.py         # YouTube comment extraction
│   ├── web_service.py         # FastAPI web service
│   ├── main.py               # Main application entry point
│   ├── example_frontend.html  # Example web interface
│   ├── toxicity.h5           # Trained model (you provide)
│   └── vectorizer.pkl        # Text vectorizer (you provide)
├── requirements.txt          # Python dependencies
├── .env.example             # Environment configuration template
└── README.md               # This file
```

## Development

### Running in Development Mode

```bash
python model/main.py web --reload
```

### Testing

```bash
# Test single comment analysis
curl -X POST "http://localhost:8000/analyze/comment" \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test comment", "threshold": 0.5}'

# Test health endpoint
curl http://localhost:8000/health
```

### Adding Custom Features

The system is designed to be extensible:

1. **Custom Models**: Replace `toxicity.h5` and `vectorizer.pkl` with your own trained models
2. **Additional APIs**: Add new endpoints in `web_service.py`
3. **New Data Sources**: Create modules similar to `youtube_api.py` for other platforms
4. **Custom Frontends**: Use the API with any frontend framework

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
WORKDIR /app/model

EXPOSE 8000
CMD ["python", "main.py", "web", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment

The service can be deployed to:
- **Heroku**: Use the included `Procfile`
- **AWS Lambda**: With minor modifications for serverless
- **Google Cloud Run**: Container-based deployment
- **Azure Container Instances**: Direct container deployment

## Model Requirements

The system expects:

1. **Toxicity Model** (`toxicity.h5`): A Keras/TensorFlow model that:
   - Takes vectorized text input
   - Outputs probabilities for 6 toxicity categories: `['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']`

2. **Vectorizer** (`vectorizer.pkl`): A pickled text vectorizer that:
   - Transforms raw text into model-compatible format
   - Must be compatible with the trained model

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Specify your license here]

## Support

For issues and questions:
1. Check the [Issues](link-to-issues) section
2. Review the API documentation at `/docs` when running the service
3. Contact the development team

## Changelog

### v1.0.0
- Initial release with YouTube comment analysis
- FastAPI web service
- Command-line interface
- Example web frontend
- Comprehensive documentation


