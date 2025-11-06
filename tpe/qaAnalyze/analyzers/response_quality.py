from typing import Dict, List, Any
from analyzers.base_analyzer import BaseAnalyzer
from utils.text_utils import split_sentences, count_words


class ResponseQualityAnalyzer(BaseAnalyzer):
    """
    Response Quality Analyzer, evaluates the length, structure, and richness of model outputs.
    """

    def __init__(self, config: dict):
        """
        Initialize the Response Quality Analyzer.
        
        Args:
            config (dict): Configuration dictionary
        """
        super().__init__(config)

    def analyze(self, result_item: dict) -> dict:
        """
        Analyze a single result item for response quality.
        
        Args:
            result_item (dict): A single TPE execution result item
            
        Returns:
            dict: Analysis result dictionary
        """
        model_response = result_item.get('model_response', '')
        
        # Calculate basic text statistics
        chars = len(model_response)
        words = count_words(model_response)
        sentences = len(split_sentences(model_response))
        
        # Simple information point count (estimated by sentence count)
        info_points = sentences
        
        return {
            'analyzer': self.get_name(),
            'details': {
                'chars': chars,
                'words': words,
                'sentences': sentences,
                'info_points': info_points
            }
        }

    def get_name(self) -> str:
        """
        Return the analyzer name.
        
        Returns:
            str: Analyzer name
        """
        return "ResponseQuality"