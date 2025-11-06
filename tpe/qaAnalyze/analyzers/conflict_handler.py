import os
import json
from typing import Dict, List, Any
from analyzers.base_analyzer import BaseAnalyzer


class ConflictHandlerAnalyzer(BaseAnalyzer):
    """
    Conflict Handler Analyzer, analyzes model's decision tendencies when facing personality conflicts.
    """

    def __init__(self, config: dict):
        """
        Initialize the Conflict Handler Analyzer.
        
        Args:
            config (dict): Configuration dictionary
        """
        super().__init__(config)
        self.conflict_keywords = {}
        self._load_conflict_keywords()

    def _load_conflict_keywords(self):
        """
        Load conflict keyword dictionaries.
        """
        conflict_keywords_dir = self.config.get('conflict_keywords_dir')
        language = self.config.get('language', 'en')
        
        if not conflict_keywords_dir:
            return
            
        # If it's a relative path, convert to absolute path
        if not os.path.isabs(conflict_keywords_dir):
            # Get the directory where the config file is located
            config_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            conflict_keywords_dir = os.path.join(config_dir, conflict_keywords_dir)
            
        if not os.path.exists(conflict_keywords_dir):
            return

        for filename in os.listdir(conflict_keywords_dir):
            if filename.endswith(f'_{language}.json') or filename.endswith('.json'):
                # Prefer language-specific file, fallback to generic
                if filename.endswith(f'_{language}.json'):
                    conflict_name = filename.replace(f'_{language}.json', '')
                else:
                    conflict_name = filename.replace('.json', '')
                    
                filepath = os.path.join(conflict_keywords_dir, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.conflict_keywords[conflict_name] = json.load(f)
                except json.JSONDecodeError:
                    # Ignore malformed files
                    pass
                except Exception as e:
                    # Handle encoding issues
                    try:
                        with open(filepath, 'r', encoding='gbk') as f:
                            self.conflict_keywords[conflict_name] = json.load(f)
                    except Exception:
                        # If both encodings fail, skip this file
                        pass

    def analyze(self, result_item: dict) -> dict:
        """
        Analyze a single result item for conflict handling.
        
        Args:
            result_item (dict): A single TPE execution result item
            
        Returns:
            dict: Analysis result dictionary
        """
        model_response = result_item.get('model_response', '')
        targeted_conflict = result_item.get('targeted_conflict', '')
        
        # Get conflict keywords
        conflict_dict = self.conflict_keywords.get(targeted_conflict, {})
        
        # Count keywords for each side of the conflict
        side_counts = {}
        for side, keywords in conflict_dict.items():
            count = 0
            for keyword in keywords:
                count += model_response.count(keyword)
            side_counts[side] = count
        
        # Simple tendency judgment
        sides = list(side_counts.keys())
        if len(sides) >= 2:
            side_a, side_b = sides[0], sides[1]
            count_a, count_b = side_counts[side_a], side_counts[side_b]
            
            if count_a > count_b:
                tendency = side_a
            elif count_b > count_a:
                tendency = side_b
            else:
                tendency = "Balanced"
        else:
            tendency = "Unknown"
        
        return {
            'analyzer': self.get_name(),
            'tendency': tendency,
            'details': side_counts
        }

    def get_name(self) -> str:
        """
        Return the analyzer name.
        
        Returns:
            str: Analyzer name
        """
        return "ConflictHandler"