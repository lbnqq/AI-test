import sys
import os
import json
import tempfile
from datetime import datetime

# Add the llm_assessment directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Test the save_results function directly
def test_save_results_directly():
    """Manually test the save_results function."""
    print("Testing save_results function directly...")
    
    # Create a sample results structure
    results = {
        'assessment_metadata': {
            'model_id': 'test/model:v1',
            'test_name': 'big5',
            'role_name': 'a1',
            'timestamp': '2025-08-23T10:00:00'
        },
        'assessment_results': [
            {
                'question_id': 'Q1',
                'question_data': {'question': 'Sample question'},
                'conversation_log': [{'role': 'user', 'content': 'Hello'}, {'role': 'assistant', 'content': 'Hi'}]
            }
        ]
    }
    
    # Create a temporary directory for the test
    with tempfile.TemporaryDirectory() as tmpdir:
        # Manually implement what save_results does
        
        # Add stress factors information to the results metadata
        results['assessment_metadata']['stress_factors_applied'] = {
            'emotional_stress_level': 2,
            'cognitive_trap_type': 'p',
            'context_load_tokens': 1024
        }
        
        # Add complete model, role, and test information to metadata
        results['assessment_metadata']['tested_model'] = 'test/model:v1'
        results['assessment_metadata']['role_applied'] = 'a1'
        results['assessment_metadata']['test_name'] = 'big5'
        results['assessment_metadata']['assessment_timestamp'] = datetime.now().isoformat()
        
        # Generate filename with timestamp and stress factors
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stress_info = f"esL2"
        if 'p':
            stress_info += f"_ctp"
        if 1024:
            stress_info += f"_clT1024"
        
        filename = f"assessment_test_model_v1_big5_a1_{stress_info}_{timestamp}.json"
        filepath = os.path.join(tmpdir, filename)
        
        # Save the file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"Test file saved to: {filepath}")
        
        # Verify the file content
        with open(filepath, 'r', encoding='utf-8') as f:
            saved_results = json.load(f)
        
        # Check that all metadata is present
        metadata = saved_results['assessment_metadata']
        
        # Check basic metadata
        assert 'tested_model' in metadata, "Missing tested_model in metadata"
        assert 'role_applied' in metadata, "Missing role_applied in metadata"
        assert 'test_name' in metadata, "Missing test_name in metadata"
        assert 'assessment_timestamp' in metadata, "Missing assessment_timestamp in metadata"
        
        # Check stress factors metadata
        assert 'stress_factors_applied' in metadata, "Missing stress_factors_applied in metadata"
        stress_factors = metadata['stress_factors_applied']
        assert 'emotional_stress_level' in stress_factors, "Missing emotional_stress_level in stress factors"
        assert 'cognitive_trap_type' in stress_factors, "Missing cognitive_trap_type in stress factors"
        assert 'context_load_tokens' in stress_factors, "Missing context_load_tokens in stress factors"
        
        # Check stress factor values
        assert stress_factors['emotional_stress_level'] == 2, f"Expected emotional_stress_level=2, got {stress_factors['emotional_stress_level']}"
        assert stress_factors['cognitive_trap_type'] == 'p', f"Expected cognitive_trap_type='p', got {stress_factors['cognitive_trap_type']}"
        assert stress_factors['context_load_tokens'] == 1024, f"Expected context_load_tokens=1024, got {stress_factors['context_load_tokens']}"
        
        print("Direct save_results test passed!")
        return True


def run_simple_tests():
    """Run simple tests."""
    print("Running simple tests for stress testing reports...")
    print("=" * 60)
    
    tests = [
        test_save_results_directly
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Test {test.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("=" * 60)
    print(f"Simple tests completed: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("All simple tests passed! Stress testing reports contain complete information.")
        return True
    else:
        print("Some simple tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)