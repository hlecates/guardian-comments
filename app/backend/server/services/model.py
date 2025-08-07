from typing import List, Dict
import pickle
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model

LABELS = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']


class ModelService:
    def __init__(self, model_path: str, tokenizer_path: str, max_sequence_length: int = 200):
        self.model = load_model(model_path)
        with open(tokenizer_path, 'rb') as f:
            self.vectorizer = pickle.load(f)
        self.max_sequence_length = max_sequence_length
        # Detect mode: Keras Tokenizer vs callable vectorizer (e.g., TextVectorization)
        if hasattr(self.vectorizer, 'texts_to_sequences'):
            self._mode = 'keras_tokenizer'
        elif callable(self.vectorizer):
            self._mode = 'callable_vectorizer'
        else:
            raise ValueError("Unsupported vectorizer type: expected Keras Tokenizer or callable vectorizer")

    def preprocess(self, texts: List[str]):
        cleaned = [t.strip() if isinstance(t, str) else "" for t in texts]
        if self._mode == 'keras_tokenizer':
            sequences = self.vectorizer.texts_to_sequences(cleaned)
            padded = pad_sequences(
                sequences,
                maxlen=self.max_sequence_length,
                padding='post',
                truncating='post'
            )
            return padded
        # callable vectorizer returns directly suitable tensors/arrays
        return self.vectorizer(cleaned)

    def score(self, texts: List[str]) -> List[Dict[str, float]]:
        X = self.preprocess(texts)
        preds = self.model.predict(X, verbose=0)
        if preds.ndim == 1:
            preds = preds.reshape(-1, 1)
        if preds.shape[1] == 1:
            return [{"toxic": float(p[0])} for p in preds]
        num_outputs = preds.shape[1]
        mapped_labels = LABELS[:num_outputs]
        results: List[Dict[str, float]] = []
        for row in preds:
            results.append({label: float(score) for label, score in zip(mapped_labels, row)})
        return results 