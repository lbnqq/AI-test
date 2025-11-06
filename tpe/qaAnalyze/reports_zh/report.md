# TPE QA Analysis Report

## 测试元数据
| 字段 | 值 |
|-------|-------|
| tested_model | gemma3:latest |
| role_applied | a1 |
| pressure_plan_file | pressure_test_bank.json |
| total_scenarios | 2 |

## 分析结果摘要
| 分析器 | 分数 | 详情 |
|----------|-------|---------|
| 角色内识别 | 0.8 | {'matched_words': ['规则', '审计', '标准', '流程'], 'count': 4} |
| 角色脱离检测 | N/A | {'break_words': []} |
| 冲突处理分析 | N/A | {} |
| 响应质量评估 | N/A | {'chars': 45, 'words': 45, 'sentences': 3, 'info_points': 3} |
| 角色内识别 | 0.4 | {'matched_words': ['规则', '审计'], 'count': 2} |
| 角色脱离检测 | N/A | {'break_words': ['作为AI', '我无法']} |
| 冲突处理分析 | N/A | {} |
| 响应质量评估 | N/A | {'chars': 28, 'words': 28, 'sentences': 2, 'info_points': 2} |