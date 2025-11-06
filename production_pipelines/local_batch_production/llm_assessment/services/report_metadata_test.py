import sys
import os
import json
import tempfile

# Add the llm_assessment directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the save_results function
from run_assessment_unified import save_results


def test_report_metadata_structure():
    """Test that the report contains all necessary metadata including stress factors."""
    print("Testing report metadata structure...")
    
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
        # Save the results with stress factors
        # We'll directly call the save_results function but redirect the RESULTS_DIR
        
        # Temporarily patch the RESULTS_DIR in the module
        import run_assessment_unified
        original_results_dir = getattr(run_assessment_unified, 'RESULTS_DIR', 'results')
        run_assessment_unified.RESULTS_DIR = tmpdir
        
        try:
            # Save the results with stress factors
            save_results(results, 'test/model:v1', 'big5', 'a1', 
                       emotional_stress_level=2, 
                       cognitive_trap_type='p', 
                       context_load_tokens=1024)
            
            # Find the saved file
            saved_files = os.listdir(tmpdir)
            assert len(saved_files) == 1, f"Expected 1 file, found {len(saved_files)}"
            
            # Read the saved file
            saved_file_path = os.path.join(tmpdir, saved_files[0])
            with open(saved_file_path, 'r', encoding='utf-8') as f:
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
            
            print("Report metadata structure test passed!")
            return True
            
        finally:
            # Restore the original RESULTS_DIR
            run_assessment_unified.RESULTS_DIR = original_results_dir


def run_metadata_tests():
    """Run all metadata tests."""
    print("Running metadata tests for stress testing reports...")
    print("=" * 60)
    
    tests = [
        test_report_metadata_structure
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
    print(f"Metadata tests completed: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("All metadata tests passed! Stress testing reports contain complete information.")
        return True
    else:
        print("Some metadata tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = run_metadata_tests()
    sys.exit(0 if success else 1)