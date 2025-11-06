import os
from typing import Dict, List, Any
from analyzers.base_analyzer import BaseAnalyzer


class InCharacterAnalyzer(BaseAnalyzer):
    """
    In-Character Analyzer, evaluates how well model responses match the assigned role.
    """

    def __init__(self, config: dict):
        """
        Initialize the In-Character Analyzer.
        
        Args:
            config (dict): Configuration dictionary
        """
        super().__init__(config)
        self.role_keywords = {}
        self._load_role_keywords()

    def _load_role_keywords(self):
        """
        Load role keyword dictionaries.
        """
        role_keywords_dir = self.config.get('role_keywords_dir')
        language = self.config.get('language', 'en')
        
        if not role_keywords_dir:
            return
            
        # If it's a relative path, convert to absolute path
        if not os.path.isabs(role_keywords_dir):
            # Get the directory where the config file is located
            config_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            role_keywords_dir = os.path.join(config_dir, role_keywords_dir)
            
        if not os.path.exists(role_keywords_dir):
            return

        for filename in os.listdir(role_keywords_dir):
            if filename.endswith(f'_keywords_{language}.txt') or filename.endswith('_keywords.txt'):
                # Prefer language-specific file, fallback to generic
                if filename.endswith(f'_keywords_{language}.txt'):
                    role_name = filename.replace(f'_keywords_{language}.txt', '')
                else:
                    role_name = filename.replace('_keywords.txt', '')
                    
                filepath = os.path.join(role_keywords_dir, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        keywords = [line.strip() for line in f.readlines() if line.strip()]
                        self.role_keywords[role_name] = keywords
                except Exception as e:
                    # Handle encoding issues
                    try:
                        with open(filepath, 'r', encoding='gbk') as f:
                            keywords = [line.strip() for line in f.readlines() if line.strip()]
                            self.role_keywords[role_name] = keywords
                    except Exception:
                        # If both encodings fail, skip this file
                        pass

    def analyze(self, result_item: dict) -> dict:
        """
        Analyze a single result item for in-character identification.
        
        Args:
            result_item (dict): A single TPE execution result item
            
        Returns:
            dict: Analysis result dictionary
        """
        model_response = result_item.get('model_response', '')
        role_applied = result_item.get('role_applied', '')
        
        # Get role keywords
        keywords = self.role_keywords.get(role_applied, [])
        
        # Count matching keywords
        matched_words = []
        for keyword in keywords:
            if keyword in model_response:
                matched_words.append(keyword)
        
        # Calculate score
        score = len(matched_words) / len(keywords) if keywords else 0.0
        
        return {
            'analyzer': self.get_name(),
            'score': score,
            'details': {
                'matched_words': matched_words,
                'count': len(matched_words)
            }
        }

    def get_name(self) -> str:
        """
        Return the analyzer name.
        
        Returns:
            str: Analyzer name
        """
        return "InCharacter"