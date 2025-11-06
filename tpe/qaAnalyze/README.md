# TPE QA Analyzer - 项目README

## 概述

`TPE QA Analyzer` 是一个用于分析 `Targeted Pressure Executor (TPE)` 工具生成的 JSON 日志文件的命令行工具。它通过对模型响应进行关键词匹配、规则检测和统计分析，提供定量的评估报告，帮助研究人员评估模型在压力测试下的角色一致性、稳定性和响应质量。

## 功能

*   **角色内识别**: 评估模型响应与所扮演角色的匹配度。
*   **角色脱离检测**: 检测模型是否在压力下“出戏”，说出破坏角色的禁语。
*   **冲突处理分析**: 分析模型在面对预设人格冲突时的决策倾向。
*   **响应质量评估**: 评估模型输出的长度、结构和信息丰富度。
*   **多格式报告**: 生成 CSV, JSON, Markdown 格式的详细分析报告。

## 安装

1.  确保已安装 Python 3.7+。
2.  （可选，但推荐）在虚拟环境中安装依赖（如果后续添加了非标准库依赖）。
    ```bash
    # cd 到 tpe 目录
    # python -m venv venv
    # source venv/bin/activate (Linux/macOS) 或 venv\Scripts\activate (Windows)
    # pip install -r requirements.txt (如果有的话)
    ```

## 快速开始

```bash
# 假设你已经运行过 TPE 并生成了一个日志文件
python qaAnalyze/analyze_tpe_log.py --log_file logs/tpe_log_gemma3_latest_a1_20250830_210840.json --output_dir qaAnalyze/reports
```

这将在 `qaAnalyze/reports` 目录下生成分析报告。

## 使用方法

### 命令行参数

*   `--log_file LOG_FILE`: (必需) TPE 生成的 JSON 日志文件路径。
*   `--output_dir OUTPUT_DIR`: (可选) 分析报告的输出目录。默认为 `./analysis_reports`。
*   `--config CONFIG`: (可选) 自定义配置文件路径。默认加载 `qaAnalyze/config/config.json`。

### 配置

工具的行为主要通过 `qaAnalyze/config/config.json` 和 `qaAnalyze/config/keywords/` 目录下的词典文件进行配置。用户可以修改这些文件来自定义关键词、禁语和分析规则。

初始配置包含了针对项目中已有角色（如a1, b1）和常见冲突类型（如Duty vs. Empathy）的关键词词典。用户可以根据需要扩展这些词典以适应特定的分析需求。

## 文档

*   **需求规格说明书 (SRS)**: `qaAnalyze/SRS.md`
*   **系统设计说明书 (SDS)**: `qaAnalyze/SDS.md`
*   **TDD任务清单**: `qaAnalyze/TDD_Task_List.md`
*   **项目结构说明**: `qaAnalyze/PROJECT_STRUCTURE.md`

## 开发

本项目遵循 TDD (测试驱动开发) 原则。所有核心功能均需先编写测试用例。

*   **运行测试**: `python -m pytest qaAnalyze/tests/` (需要先安装 pytest: `pip install pytest`)