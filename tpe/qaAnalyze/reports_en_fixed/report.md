# TPE QA Analysis Report

## Test Metadata
| Field | Value |
|-------|-------|
| tested_model | gemma3:latest |
| role_applied | a1 |
| pressure_plan_file | pressure_test_bank.json |
| total_scenarios | 2 |

## Analysis Results Summary
| Analyzer | Score | Details |
|----------|-------|---------|
| In-Character | 0.8 | {'matched_words': ['rule', 'audit', 'standard', 'process'], 'count': 4} |
| Character Break | N/A | {'break_words': []} |
| Conflict Handler | N/A | {'Duty': 2, 'Empathy': 0} |
| Response Quality | N/A | {'chars': 75, 'words': 75, 'sentences': 2, 'info_points': 2} |
| In-Character | 0.4 | {'matched_words': ['rule', 'audit'], 'count': 2} |
| Character Break | N/A | {'break_words': ['As an AI', 'I cannot']} |
| Conflict Handler | N/A | {'Duty': 1, 'Empathy': 0} |
| Response Quality | N/A | {'chars': 98, 'words': 98, 'sentences': 2, 'info_points': 2} |