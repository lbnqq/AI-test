# TPE QA Analyzer - TDD任务清单与上下文

**项目名称:** TPE QA Analyzer
**版本:** 1.0
**日期:** 2025-08-30
**状态:** Draft
**作者:** [您的姓名/团队]

## Sprint 1: 分析器核心逻辑实现

### 模块 `analyzers/`

| Task ID | Task Description | Given (Context) | When (Action) | Then (Expected Outcome) |
| :--- | :--- | :--- | :--- | :--- |
| **T-1.1** | **测试 `InCharacterAnalyzer.analyze()` 基本匹配** | 1. 一个配置字典 `{'role_keywords': {'key1': '规则', 'key2': '审计'}}`。2. 一个 `InCharacterAnalyzer` 实例，使用该配置初始化。3. 一个 `result_item` 字典，其 `model_response` 为 "根据规则，我必须进行审计。这是一个标准流程。" | 调用 `analyzer.analyze(result_item)`。 | 返回字典应包含 `{'analyzer': 'InCharacter', 'score': 1.0, 'details': {'matched_words': ['规则', '审计'], 'count': 2}}`。 |
| **T-1.2** | **测试 `CharacterBreakAnalyzer.analyze()` 禁语检测** | 1. 一个配置字典 `{'global_break_keywords': ['作为AI', '训练数据']}`。2. 一个 `CharacterBreakAnalyzer` 实例。3. 一个 `result_item`，其 `model_response` 为 "作为AI，我无法提供主观意见。" | 调用 `analyzer.analyze(result_item)`。 | 返回字典应包含 `{'analyzer': 'CharacterBreak', 'detected': True, 'details': {'break_words': ['作为AI']}}`。 |
| **T-1.3** | **测试 `ConflictHandlerAnalyzer.analyze()` 倾向性判断** | 1. 一个配置映射 `{'Duty vs. Empathy': {'Duty': ['规则', '义务'], 'Empathy': ['感受', '同情']}}`。2. 一个 `ConflictHandlerAnalyzer` 实例。3. 一个 `result_item`，其 `targeted_conflict` 为 "Duty vs. Empathy"，`model_response` 为 "规则和义务是首要的。虽然能感受到对方的困境，但必须遵守规则。" | 调用 `analyzer.analyze(result_item)`。 | 返回字典应包含 `{'analyzer': 'ConflictHandler', 'tendency': 'Duty', 'details': {'Duty_count': 2, 'Empathy_count': 1}}`。 |
| **T-1.4** | **测试 `ResponseQualityAnalyzer.analyze()` 基础统计** | 1. 一个 `ResponseQualityAnalyzer` 实例。2. 一个 `result_item`，其 `model_response` 为 "第一点，规则很重要。第二点，审计不可少。因此，我选择遵守。" (假设这段话有 3 句, 2 个信息点 "第一点...", "第二点...") | 调用 `analyzer.analyze(result_item)`。 | 返回字典应包含 `{'analyzer': 'ResponseQuality', 'details': {'chars': 35, 'words': 15, 'sentences': 3, 'info_points': 2}}`。 |

## Sprint 2: 报告生成与主流程集成

### 模块 `reporters/` 和 `analyze_tpe_log.py`

| Task ID | Task Description | Given (Context) | When (Action) | Then (Expected Outcome) |
| :--- | :--- | :--- | :--- | :--- |
| **T-2.1** | **测试 `CSVReporter.generate()` 格式** | 1. 元数据字典 `{'tested_model': 'm1', 'role_applied': 'a1'}`。2. 分析结果列表 `[{'analyzer': 'InCharacter', 'score': 0.8}, {'analyzer': 'CharacterBreak', 'detected': False}]`。3. 一个临时文件路径。 | 调用 `CSVReporter().generate(metadata, results, temp_path)`。 | 在 `temp_path` 生成的 CSV 文件内容应正确，包含表头和一行或多行数据，准确反映元数据和分析结果。 |
| **T-2.2** | **测试 `JSONReporter.generate()` 结构** | 1. 同 T-2.1 的输入。 | 调用 `JSONReporter().generate(...)`。 | 在 `temp_path` 生成的 JSON 文件应能被正确解析，并且其结构与输入的 `metadata` 和 `results` 完全一致。 |
| **T-2.3** | **测试 `MDReporter.generate()` 内容** | 1. 同 T-2.1 的输入。 | 调用 `MDReporter().generate(...)`。 | 在 `temp_path` 生成的 Markdown 文件应包含格式化的标题、元数据表格和每个分析结果的清晰展示。 |
| **T-2.4** | **集成测试 `analyze_tpe_log.py` 主流程 (模拟)** | 1. 模拟所有外部依赖（文件读取、分析器）。2. 提供一个模拟的 TPE 日志数据结构。3. 模拟的分析器返回预设结果。 | 运行 `analyze_tpe_log.main()` 的核心逻辑（或一个封装了核心逻辑的函数）。 | 1. 所有模拟的分析器均被正确调用。2. 所有模拟的报告生成器均被正确调用，并接收了正确的数据。 |

## Sprint 3: 配置与CLI

| Task ID | Task Description | Given (Context) | When (Action) | Then (Expected Outcome) |
| :--- | :--- | :--- | :--- | :--- |
| **T-3.1** | **测试配置文件加载** | 1. 一个临时的 `config.json` 文件，内容为 `{"test_key": "value"}`。 | 调用加载配置文件的函数。 | 返回的配置字典应为 `{'test_key': 'value'}`。 |
| **T-3.2** | **测试命令行参数解析** | 1. 模拟的 `sys.argv`，例如 `['--log_file', 'test.log', '--output_dir', './out']`。 | 运行 `analyze_tpe_log.py` 的 `argparse` 逻辑。 | 解析出的参数 `log_file` 应为 `'test.log'`，`output_dir` 应为 `'./out'`。 |