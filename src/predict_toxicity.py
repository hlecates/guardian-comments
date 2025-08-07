import os
import pickle
import pandas as pd
import tensorflow as tf
import numpy as np
from typing import List, Dict, Union
import argparse


class ToxicityPredictor:

    # Toxicity categories as they appear in the data
    TOXICITY_CATEGORIES = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
    
    def __init__(self, model_path: str, vectorizer_path: str):
        self.model_path = model_path
        self.vectorizer_path = vectorizer_path
        
        # Validate file paths
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        if not os.path.isfile(vectorizer_path):
            raise FileNotFoundError(f"Vectorizer file not found: {vectorizer_path}")
        
        # Load model and vectorizer
        print(f"Loading model from: {model_path}")
        self.model = tf.keras.models.load_model(model_path)
        
        print(f"Loading vectorizer from: {vectorizer_path}")
        with open(vectorizer_path, 'rb') as f:
            self.vectorizer = pickle.load(f)
    
    def predict(self, comments: Union[str, List[str]], threshold: float = 0.5) -> Union[Dict, List[Dict]]:
        # Handle single comment
        if isinstance(comments, str):
            comments = [comments]
            single_comment = True
        else:
            single_comment = False
        
        # Vectorize the comments
        vectorized_comments = self.vectorizer(comments)
        
        # Make predictions
        predictions = self.model.predict(vectorized_comments, verbose=0)
        
        # Format results
        results = []
        for i, comment in enumerate(comments):
            result = {
                'comment': comment,
                'predictions': {},
                'any_toxic': False
            }
            
            # Add predictions for each category
            any_toxic = False
            for j, category in enumerate(self.TOXICITY_CATEGORIES):
                probability = float(predictions[i][j])
                is_toxic = probability > threshold
                
                result['predictions'][category] = {
                    'probability': probability,
                    'is_toxic': is_toxic
                }
                
                if is_toxic:
                    any_toxic = True
            
            result['any_toxic'] = any_toxic
            results.append(result)
        
        # Return single result if single comment was provided
        return results[0] if single_comment else results
    
    def predict_probabilities(self, comments: Union[str, List[str]]) -> Union[np.ndarray, np.ndarray]:
        if isinstance(comments, str):
            comments = [comments]
        
        vectorized_comments = self.vectorizer(comments)
        return self.model.predict(vectorized_comments, verbose=0)
    
    def predict_binary(self, comments: Union[str, List[str]], threshold: float = 0.5) -> Union[np.ndarray, np.ndarray]:
        probabilities = self.predict_probabilities(comments)
        return (probabilities > threshold).astype(int)


def predict_toxicity(comments: Union[str, List[str]], 
                    model_path: str = 'toxicity.h5', 
                    vectorizer_path: str = 'vectorizer.pkl',
                    threshold: float = 0.5) -> Union[Dict, List[Dict]]:

    predictor = ToxicityPredictor(model_path, vectorizer_path)
    return predictor.predict(comments, threshold)


def main():
    parser = argparse.ArgumentParser(description='Predict toxicity in comments')
    parser.add_argument('--input', '-i', type=str, help='Input file with comments (one per line)')
    parser.add_argument('--comment', '-c', type=str, help='Single comment to predict')
    parser.add_argument('--model', '-m', type=str, default='toxicity.h5', 
                       help='Path to model file (default: toxicity.h5)')
    parser.add_argument('--vectorizer', '-v', type=str, default='vectorizer.pkl',
                       help='Path to vectorizer file (default: vectorizer.pkl)')
    parser.add_argument('--threshold', '-t', type=float, default=0.5,
                       help='Classification threshold (default: 0.5)')
    parser.add_argument('--output', '-o', type=str, help='Output file for results (optional)')
    parser.add_argument('--format', '-f', choices=['json', 'csv', 'simple'], default='simple',
                       help='Output format (default: simple)')
    
    args = parser.parse_args()
    
    # Validate input
    if not args.input and not args.comment:
        parser.error("Must provide either --input file or --comment text")
    
    # Initialize predictor
    predictor = ToxicityPredictor(args.model, args.vectorizer)
    
    # Get comments
    if args.comment:
        comments = [args.comment]
    else:
        with open(args.input, 'r', encoding='utf-8') as f:
            comments = [line.strip() for line in f if line.strip()]
    
    # Make predictions
    results = predictor.predict(comments, args.threshold)
    if isinstance(results, dict):
        results = [results]
    
    # Format output
    if args.format == 'json':
        import json
        output = json.dumps(results, indent=2)
    elif args.format == 'csv':
        import pandas as pd
        rows = []
        for result in results:
            row = {'comment': result['comment'], 'any_toxic': result['any_toxic']}
            for category, pred in result['predictions'].items():
                row[f'{category}_prob'] = pred['probability']
                row[f'{category}_toxic'] = pred['is_toxic']
            rows.append(row)
        df = pd.DataFrame(rows)
        output = df.to_csv(index=False)
    else:  # simple format
        output_lines = []
        for result in results:
            comment = result['comment']
            any_toxic = "TOXIC" if result['any_toxic'] else "CLEAN"
            toxic_categories = [cat for cat, pred in result['predictions'].items() if pred['is_toxic']]
            categories_str = ", ".join(toxic_categories) if toxic_categories else "none"
            
            output_lines.append(f"{any_toxic} | {categories_str} | {comment}")
        output = "\n".join(output_lines)
    
    # Save or print output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Results saved to: {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
