import sys
import os

# Add project root directory to Python path
project_root = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from tests.test_in_character import test_in_character_analyzer
from tests.test_character_break import test_character_break_analyzer
from tests.test_conflict_handler import test_conflict_handler_analyzer
from tests.test_response_quality import test_response_quality_analyzer

if __name__ == '__main__':
    print("Running unit tests...")
    
    try:
        test_in_character_analyzer()
        print("✓ In-Character Analyzer test passed")
    except Exception as e:
        print(f"✗ In-Character Analyzer test failed: {e}")
    
    try:
        test_character_break_analyzer()
        print("✓ Character Break Analyzer test passed")
    except Exception as e:
        print(f"✗ Character Break Analyzer test failed: {e}")
    
    try:
        test_conflict_handler_analyzer()
        print("✓ Conflict Handler Analyzer test passed")
    except Exception as e:
        print(f"✗ Conflict Handler Analyzer test failed: {e}")
    
    try:
        test_response_quality_analyzer()
        print("✓ Response Quality Analyzer test passed")
    except Exception as e:
        print(f"✗ Response Quality Analyzer test failed: {e}")
    
    print("Unit tests completed.")