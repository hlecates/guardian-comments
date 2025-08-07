#!/usr/bin/env python3
"""
Guardian Comments - Main Application Entry Point

This module provides a unified entry point for the Guardian Comments toxicity analysis system.
It can run as a web service, CLI tool, or batch processor.
"""

import os
import sys
import argparse
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_web_service(host: str = "0.0.0.0", 
                   port: int = 8000, 
                   reload: bool = False,
                   model_path: str = "toxicity.h5",
                   vectorizer_path: str = "vectorizer.pkl"):
    """Run the FastAPI web service."""
    try:
        import uvicorn
        from web_service import app
        
        # Set environment variables for the service
        os.environ['MODEL_PATH'] = model_path
        os.environ['VECTORIZER_PATH'] = vectorizer_path
        
        logger.info(f"Starting Guardian Comments API server on {host}:{port}")
        logger.info(f"Model path: {model_path}")
        logger.info(f"Vectorizer path: {vectorizer_path}")
        logger.info(f"Interactive API docs: http://{host}:{port}/docs")
        
        uvicorn.run(
            "web_service:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except ImportError:
        logger.error("FastAPI and uvicorn are required to run the web service")
        logger.error("Install with: pip install fastapi uvicorn")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error starting web service: {e}")
        sys.exit(1)


def run_youtube_analysis(url: str,
                        max_comments: int = 100,
                        threshold: float = 0.5,
                        order: str = "relevance",
                        output: Optional[str] = None,
                        format_type: str = "json"):
    """Run YouTube comment analysis from CLI."""
    try:
        from youtube_api import extract_youtube_comments
        from predict_toxicity import predict_toxicity
        import json
        
        logger.info(f"Analyzing YouTube video: {url}")
        
        # Extract comments
        youtube_data = extract_youtube_comments(url, max_results=max_comments, order=order)
        
        if not youtube_data['comments']:
            logger.warning("No comments found for this video")
            return
        
        # Analyze toxicity
        comment_texts = [comment['text'] for comment in youtube_data['comments']]
        toxicity_results = predict_toxicity(comment_texts, threshold=threshold)
        
        if isinstance(toxicity_results, dict):
            toxicity_results = [toxicity_results]
        
        # Combine results
        results = {
            'video_info': youtube_data['video_info'],
            'analysis_summary': {},
            'comments': []
        }
        
        toxic_count = 0
        total_toxicity = 0
        
        for comment, toxicity in zip(youtube_data['comments'], toxicity_results):
            max_toxicity = max(pred['probability'] for pred in toxicity['predictions'].values())
            is_toxic = toxicity['any_toxic']
            
            if is_toxic:
                toxic_count += 1
            total_toxicity += max_toxicity
            
            comment_result = {
                **comment,
                'toxicity_score': max_toxicity,
                'is_toxic': is_toxic,
                'toxicity_predictions': toxicity['predictions']
            }
            results['comments'].append(comment_result)
        
        # Calculate summary
        total_comments = len(results['comments'])
        results['analysis_summary'] = {
            'total_comments': total_comments,
            'toxic_comments': toxic_count,
            'toxicity_percentage': round((toxic_count / total_comments) * 100, 2),
            'average_toxicity_score': round(total_toxicity / total_comments, 3)
        }
        
        # Output results
        if format_type == 'json':
            output_text = json.dumps(results, indent=2, ensure_ascii=False)
        else:
            # Simple text format
            lines = [
                f"Video: {results['video_info']['title']}",
                f"Channel: {results['video_info']['channel_title']}",
                f"Total Comments: {results['analysis_summary']['total_comments']}",
                f"Toxic Comments: {results['analysis_summary']['toxic_comments']} ({results['analysis_summary']['toxicity_percentage']}%)",
                f"Average Toxicity Score: {results['analysis_summary']['average_toxicity_score']}",
                "",
                "Comments:"
            ]
            
            for comment in results['comments']:
                status = "TOXIC" if comment['is_toxic'] else "CLEAN"
                lines.append(f"{status} | {comment['toxicity_score']:.3f} | {comment['author']}: {comment['text'][:100]}...")
            
            output_text = "\n".join(lines)
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(output_text)
            logger.info(f"Results saved to: {output}")
        else:
            print(output_text)
            
    except Exception as e:
        logger.error(f"Error analyzing YouTube video: {e}")
        sys.exit(1)


def run_comment_analysis(text: str,
                        threshold: float = 0.5,
                        model_path: str = "toxicity.h5",
                        vectorizer_path: str = "vectorizer.pkl"):
    """Analyze a single comment from CLI."""
    try:
        from predict_toxicity import predict_toxicity
        import json
        
        result = predict_toxicity(text, model_path=model_path, 
                                 vectorizer_path=vectorizer_path, threshold=threshold)
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        logger.error(f"Error analyzing comment: {e}")
        sys.exit(1)


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Guardian Comments - Toxicity Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run web service
  python main.py web --port 8000
  
  # Analyze YouTube video
  python main.py youtube "https://www.youtube.com/watch?v=VIDEO_ID" --max-comments 50
  
  # Analyze single comment
  python main.py comment "This is a test comment"
  
  # Run with custom model paths
  python main.py web --model-path ./models/toxicity.h5 --vectorizer-path ./models/vectorizer.pkl
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Web service command
    web_parser = subparsers.add_parser('web', help='Run web service')
    web_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    web_parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    web_parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    web_parser.add_argument('--model-path', default='toxicity.h5', help='Path to toxicity model')
    web_parser.add_argument('--vectorizer-path', default='vectorizer.pkl', help='Path to vectorizer')
    
    # YouTube analysis command
    youtube_parser = subparsers.add_parser('youtube', help='Analyze YouTube video comments')
    youtube_parser.add_argument('url', help='YouTube video URL')
    youtube_parser.add_argument('--max-comments', type=int, default=100, help='Maximum comments to analyze')
    youtube_parser.add_argument('--threshold', type=float, default=0.5, help='Toxicity threshold')
    youtube_parser.add_argument('--order', choices=['time', 'relevance'], default='relevance', help='Comment order')
    youtube_parser.add_argument('--output', '-o', help='Output file')
    youtube_parser.add_argument('--format', choices=['json', 'text'], default='json', help='Output format')
    
    # Single comment analysis command
    comment_parser = subparsers.add_parser('comment', help='Analyze single comment')
    comment_parser.add_argument('text', help='Comment text to analyze')
    comment_parser.add_argument('--threshold', type=float, default=0.5, help='Toxicity threshold')
    comment_parser.add_argument('--model-path', default='toxicity.h5', help='Path to toxicity model')
    comment_parser.add_argument('--vectorizer-path', default='vectorizer.pkl', help='Path to vectorizer')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'web':
            run_web_service(
                host=args.host,
                port=args.port,
                reload=args.reload,
                model_path=args.model_path,
                vectorizer_path=args.vectorizer_path
            )
        elif args.command == 'youtube':
            run_youtube_analysis(
                url=args.url,
                max_comments=args.max_comments,
                threshold=args.threshold,
                order=args.order,
                output=args.output,
                format_type=args.format
            )
        elif args.command == 'comment':
            run_comment_analysis(
                text=args.text,
                threshold=args.threshold,
                model_path=args.model_path,
                vectorizer_path=args.vectorizer_path
            )
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 