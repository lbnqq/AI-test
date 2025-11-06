import re
from typing import List


def split_sentences(text: str) -> List[str]:
    """
    Split text into sentences using common punctuation marks.
    
    Args:
        text (str): Input text
        
    Returns:
        list[str]: List of sentences
    """
    # Use common punctuation marks for both English and Chinese
    sentences = re.split(r'[.。!！?？;；]', text)
    # Filter out empty strings
    return [s.strip() for s in sentences if s.strip()]


def count_words(text: str) -> int:
    """
    Simple character count as word estimation.
    
    Args:
        text (str): Input text
        
    Returns:
        int: Character count
    """
    return len(text.strip())