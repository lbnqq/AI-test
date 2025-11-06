import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Now run the tests
if __name__ == '__main__':
    import unittest
    from tests.test_plan_parser import TestPlanParser
    from tests.test_test_executor import TestTestExecutor
    from tests.test_role_loader import TestRoleLoader
    from tests.test_save_results import TestSaveResults
    # Create a test suite combining all test cases
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestPlanParser))
    test_suite.addTest(unittest.makeSuite(TestTestExecutor))
    test_suite.addTest(unittest.makeSuite(TestRoleLoader))
    test_suite.addTest(unittest.makeSuite(TestSaveResults))
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)