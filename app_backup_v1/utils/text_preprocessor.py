import os
import chardet
import spacy
from typing import Dict, List, Optional

class TextPreprocessor:
    def __init__(self):
        self.nlp = spacy.load('el_core_news_md')  # Greek language model
        self.texts = {}
        
    def load_text(self, file_path: str) -> Optional[str]:
        """Load a single text file with automatic encoding detection"""
        try:
            # Detect encoding
            with open(file_path, 'rb') as f:
                raw = f.read()
                encoding = chardet.detect(raw)['encoding']
            
            # Read with detected encoding
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")
            return None
    
    def process_text(self, text: str) -> spacy.tokens.Doc:
        """Process text using spaCy"""
        return self.nlp(text.lower())
    
    def load_directory(self, directory: str) -> Dict[str, spacy.tokens.Doc]:
        """Load and process all texts from a directory"""
        for filename in os.listdir(directory):
            if filename.endswith('.txt'):
                file_path = os.path.join(directory, filename)
                text = self.load_text(file_path)
                if text:
                    self.texts[filename] = self.process_text(text)
        return self.texts
    
    def get_processed_texts(self) -> Dict[str, spacy.tokens.Doc]:
        """Get all processed texts"""
        return self.texts