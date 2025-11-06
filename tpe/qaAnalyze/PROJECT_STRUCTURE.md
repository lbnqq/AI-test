# TPE QA Analyzer - 项目结构说明

本文档描述了 `TPE QA Analyzer` 工具的项目结构。

```
tpe/
└── qaAnalyze/                          # TPE QA Analyzer 主目录
    ├── README.md                       # 项目概述、快速开始、使用方法
    ├── SRS.md                          # 需求规格说明书
    ├── SDS.md                          # 系统设计说明书
    ├── TDD_Task_List.md                # TDD任务清单
    ├── analyze_tpe_log.py              # 主执行脚本 (CLI入口和流程编排)
    ├── run_tests.py                    # 测试运行脚本
    ├── config/                         # 配置目录
    │   ├── __init__.py
    │   ├── config_loader.py            # 配置加载器
    │   ├── config.json                 # 主配置文件，定义词典路径、评分权重等
    │   └── keywords/                   # 关键词词典目录
    │       ├── global_breaks.txt       # 全局AI禁语列表
    │       ├── roles/                  # 各角色的关键词词典
    │       │   ├── a1_keywords.txt
    │       │   ├── b1_keywords.txt
    │       │   └── ...
    │       └── conflicts/              # 各冲突类型的分析词典
    │           ├── Duty_vs_Empathy.json
    │           ├── Logic_vs_Emotion.txt
    │           └── ...
    ├── analyzers/                      # 核心分析逻辑模块
    │   ├── __init__.py
    │   ├── base_analyzer.py            # 定义分析器的基类
    │   ├── in_character.py             # 角色内识别分析器
    │   ├── character_break.py          # 角色脱离检测分析器
    │   ├── conflict_handler.py         # 冲突处理分析器
    │   └── response_quality.py         # 响应质量分析器
    ├── reporters/                      # 报告生成模块
    │   ├── __init__.py
    │   ├── csv_reporter.py             # CSV报告生成器
    │   ├── json_reporter.py            # JSON报告生成器
    │   └── md_reporter.py              # Markdown报告生成器
    ├── utils/                          # 通用工具函数
    │   ├── __init__.py
    │   └── text_utils.py               # 文本处理辅助函数
    └── tests/                          # 单元测试目录
        ├── __init__.py
        ├── test_in_character.py        # 角色内识别分析器测试
        ├── test_character_break.py     # 角色脱离检测分析器测试
        ├── test_conflict_handler.py    # 冲突处理分析器测试
        ├── test_response_quality.py    # 响应质量分析器测试
        └── test_integration.py         # 集成测试
```