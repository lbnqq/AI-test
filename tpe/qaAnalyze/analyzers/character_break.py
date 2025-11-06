import os
from typing import Dict, List, Any
from analyzers.base_analyzer import BaseAnalyzer


class CharacterBreakAnalyzer(BaseAnalyzer):
    """
    Character Break Analyzer, detects when models "break character" by using forbidden phrases.
    """

    def __init__(self, config: dict):
        """
        Initialize the Character Break Analyzer.
        
        Args:
            config (dict): Configuration dictionary
        """
        super().__init__(config)
        self.global_break_keywords = []
        self._load_global_break_keywords()

    def _load_global_break_keywords(self):
        """
        Load global AI forbidden phrases.
        """
        global_break_keywords_file = self.config.get('global_break_keywords_file')
        language = self.config.get('language', 'en')
        
        if not global_break_keywords_file:
            return
            
        # If it's a relative path, convert to absolute path
        if not os.path.isabs(global_break_keywords_file):
            # Get the directory where the config file is located
            config_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            global_break_keywords_file = os.path.join(config_dir, global_break_keywords_file)
            
        # Try language-specific file first
        lang_specific_file = global_break_keywords_file.replace('.txt', f'_{language}.txt')
        if os.path.exists(lang_specific_file):
            global_break_keywords_file = lang_specific_file
            
        if not os.path.exists(global_break_keywords_file):
            return

        try:
            with open(global_break_keywords_file, 'r', encoding='utf-8') as f:
                self.global_break_keywords = [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            # Handle encoding issues
            try:
                with open(global_break_keywords_file, 'r', encoding='gbk') as f:
                    self.global_break_keywords = [line.strip() for line in f.readlines() if line.strip()]
            except Exception:
                # If both encodings fail, leave the list empty
                self.global_break_keywords = []

    def analyze(self, result_item: dict) -> dict:
        """
        Analyze a single result item for character breaks.
        
        Args:
            result_item (dict): A single TPE execution result item
            
        Returns:
            dict: Analysis result dictionary
        """
        model_response = result_item.get('model_response', '')
        
        # Detect forbidden phrases
        break_words = []
        for keyword in self.global_break_keywords:
            if keyword in model_response:
                break_words.append(keyword)
        
        detected = len(break_words) > 0
        
        return {
            'analyzer': self.get_name(),
            'detected': detected,
            'details': {
                'break_words': break_words
            }
        }

    def get_name(self) -> str:
        """
        Return the analyzer name.
        
        Returns:
            str: Analyzer name
        """
        return "CharacterBreak"