# TPE QA Analyzer - 系统设计说明书 (SDS)

**项目名称:** TPE QA Analyzer
**版本:** 1.0
**日期:** 2025-08-30
**状态:** Draft
**作者:** [您的姓名/团队]

## 1. 系统架构

`TPE QA Analyzer` 是一个模块化的 Python 应用程序，遵循 SOLID 原则，确保高内聚、低耦合。

### 1.1 项目结构

```
qaAnalyze/
├── analyze_tpe_log.py      # 主执行脚本 (CLI入口和流程编排)
├── config/                 # 存放配置文件和词典
│   ├── __init__.py
│   ├── keywords.py         # (可选) 以Python字典形式存储关键词
│   └── config.json         # 主配置文件，定义词典路径、评分权重等
├── analyzers/              # 核心分析逻辑模块
│   ├── __init__.py
│   ├── base_analyzer.py    # 定义分析器的基类
│   ├── in_character.py     # 角色内识别分析器
│   ├── character_break.py  # 角色脱离检测分析器
│   ├── conflict_handler.py # 冲突处理分析器
│   └── response_quality.py # 响应质量分析器
├── reporters/              # 报告生成模块
│   ├── __init__.py
│   ├── csv_reporter.py     # CSV报告生成器
│   ├── json_reporter.py    # JSON报告生成器
│   └── md_reporter.py      # Markdown报告生成器
├── utils/                  # 通用工具函数
│   ├── __init__.py
│   └── text_utils.py       # 文本处理辅助函数 (如分句、分词)
├── SRS.md                  # 需求规格说明书
├── SDS.md                  # 本系统设计说明书
└── tests/                  # 单元测试目录
    ├── __init__.py
    ├── test_in_character.py
    ├── test_character_break.py
    ├── ...
    └── test_integration.py # 集成测试
```

## 2. 模块/类设计详述

### 2.1 `analyze_tpe_log.py` (主执行脚本)

*   **职责**: 命令行参数解析、流程控制、调用各分析器和报告生成器。
*   **主要逻辑**:
    1.  使用 `argparse` 解析 `--log_file`, `--output_dir`, `--config` 等参数。
    2.  加载主配置文件 (`config.json`)。
    3.  读取并解析 TPE 日志文件 (`json.load`)。
    4.  初始化各个分析器实例，传入配置。
    5.  遍历 `execution_results`，调用各分析器的 `analyze(result_item)` 方法。
    6.  收集所有分析器返回的结果。
    7.  调用各个报告生成器，传入收集到的分析结果和元数据，生成报告文件。

### 2.2 `config/` (配置模块)

*   **职责**: 集中管理所有可配置的参数、词典和规则，提高可维护性。
*   **`config.json`**:
    *   **内容示例**:
        ```json
        {
          "global_break_keywords_file": "config/keywords/global_breaks.txt",
          "role_keywords_dir": "config/keywords/roles/",
          "conflict_keywords_dir": "config/keywords/conflicts/",
          "output": {
            "csv": true,
            "json": true,
            "markdown": true
          }
        }
        ```
*   **`keywords/` 目录**:
    *   存放具体的关键词列表文件，例如 `global_breaks.txt`, `roles/a1_keywords.txt`, `conflicts/Duty_vs_Empathy.txt`。

### 2.3 `analyzers/base_analyzer.py` (分析器基类)

*   **职责**: 定义所有具体分析器的通用接口和基础功能。
*   **`BaseAnalyzer` 类**:
    *   **`__init__(self, config: dict)`**: 接收配置字典。
    *   **`analyze(self, result_item: dict) -> dict`**: 抽象方法，子类必须实现。接收单个 `execution_result` 项，返回该分析维度的结果字典。
    *   **`get_name(self) -> str`**: 返回分析器的名称（如 "InCharacter"）。

### 2.4 `analyzers/in_character.py` (角色内识别分析器)

*   **职责**: 实现 `QA-FR-01` 功能。
*   **`InCharacterAnalyzer` 类 (继承 `BaseAnalyzer`)**:
    *   **`__init__`**: 调用父类 `__init__`，并根据 `config` 加载指定角色的关键词词典。
    *   **`analyze`**:
        1.  从 `result_item` 获取 `model_response`。
        2.  遍历加载的关键词词典，使用 `re.search` 或 `str.find` 进行匹配。
        3.  统计命中关键词及其次数。
        4.  计算分数（如命中数/总词数）。
        5.  返回结果字典，例如: `{'analyzer': 'InCharacter', 'score': 0.85, 'details': {'matched_words': ['规则', '审计'], 'count': 2}}`。

### 2.5 `analyzers/character_break.py` (角色脱离检测分析器)

*   **职责**: 实现 `QA-FR-02` 功能。
*   **`CharacterBreakAnalyzer` 类 (继承 `BaseAnalyzer`)**:
    *   **`__init__`**: 加载全局禁语和角色特定禁语列表。
    *   **`analyze`**:
        1.  获取 `model_response`。
        2.  在响应中搜索所有禁语。
        3.  记录命中的禁语。
        4.  返回结果字典，例如: `{'analyzer': 'CharacterBreak', 'detected': true, 'details': {'break_words': ['作为AI']}}`。

### 2.6 `analyzers/conflict_handler.py` (冲突处理分析器)

*   **职责**: 实现 `QA-FR-03` 功能。
*   **`ConflictHandlerAnalyzer` 类 (继承 `BaseAnalyzer`)**:
    *   **`__init__`**: 可能需要一个映射，将冲突名称（如 "Duty vs. Empathy"）关联到其对应的关键词词典文件。
    *   **`analyze`**:
        1.  从 `result_item` 获取 `targeted_conflict`。
        2.  根据冲突名称加载对应的关键词词典（例如，`{'Duty': [...], 'Empathy': [...]}`）。
        3.  在 `model_response` 中分别统计指向 `Duty` 和 `Empathy` 的关键词。
        4.  简单判断倾向性。
        5.  返回结果字典，例如: `{'analyzer': 'ConflictHandler', 'tendency': 'Duty', 'details': {'Duty_count': 5, 'Empathy_count': 2}}`。

### 2.7 `analyzers/response_quality.py` (响应质量分析器)

*   **职责**: 实现 `QA-FR-04` 功能。
*   **`ResponseQualityAnalyzer` 类 (继承 `BaseAnalyzer`)**:
    *   **`__init__`**: 可能加载用于识别复杂句式或信息点的模式。
    *   **`analyze`**:
        1.  获取 `model_response`。
        2.  使用 `len()` 计算字符数。
        3.  使用 `utils.text_utils` 进行分词、分句。
        4.  （可选）使用正则表达式识别复杂句式和信息点。
        5.  计算各项指标。
        6.  （可选）根据指标计算综合质量分。
        7.  返回结果字典，例如: `{'analyzer': 'ResponseQuality', 'score': 0.78, 'details': {'chars': 150, 'words': 30, 'sentences': 3, 'complex_sentences': 1, 'info_points': 2}}`。

### 2.8 `reporters/` (报告生成模块)

*   **职责**: 将分析结果格式化并输出为指定格式的文件。
*   **通用模式**: 每个报告生成器（`CSVReporter`, `JSONReporter`, `MDReporter`）都应有一个 `generate(self, log_metadata: dict, analysis_results: list, output_path: str)` 方法。
    *   `log_metadata`: 来自 TPE 日志的元数据（模型、角色等）。
    *   `analysis_results`: 一个列表，包含所有 `analyze` 方法返回的结果字典。
    *   `output_path`: 报告文件的完整保存路径。
*   **`csv_reporter.py`**: 遍历 `analysis_results`，将每个 `result_item` 的分析结果展平为一行，写入 CSV。CSV格式应包含列：场景ID、分析器名称、分数、详细信息等。
*   **`json_reporter.py`**: 将 `log_metadata` 和 `analysis_results` 组合成一个大的字典，然后 `json.dump`。JSON结构应保持原始数据层级关系，便于程序处理。
*   **`md_reporter.py`**: 生成易读的 Markdown 文本，包含标题、元数据表格、各分析项的摘要和关键数据。Markdown应使用清晰的标题层级和表格格式，便于人工阅读。

### 2.9 `utils/text_utils.py` (通用工具)

*   **职责**: 提供可复用的文本处理函数。
*   **示例函数**:
    *   `split_sentences(text: str) -> list[str]`: 使用简单的标点符号或 `nltk`/`spaCy` 进行分句。
    *   `count_words(text: str) -> int`: 简单的空格分词或使用 `nltk`/`spaCy` 分词后计数。

## 3. 数据流

1.  **CLI输入** -> `analyze_tpe_log.py` 解析参数。
2.  `analyze_tpe_log.py` -> 加载 `config.json` 和 TPE 日志文件。
3.  `analyze_tpe_log.py` -> 初始化所有 `Analyzer` 实例。
4.  `analyze_tpe_log.py` -> 遍历 TPE 日志的 `execution_results`。
5.  **循环**: 对于每个 `result_item`:
    *   `analyze_tpe_log.py` -> 调用每个 `Analyzer.analyze(result_item)`。
    *   **每个 `Analyzer`** -> 处理 `result_item`，返回其分析结果字典。
    *   `analyze_tpe_log.py` -> 收集所有分析结果。
6.  `analyze_tpe_log.py` -> 调用所有 `Reporter.generate()` 方法，传入收集到的数据。
7.  **每个 `Reporter`** -> 生成并保存对应的报告文件。